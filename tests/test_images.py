from pathlib import Path
from tempfile import NamedTemporaryFile

import f3d
from pytest import mark, raises

from f3d_extras.images import camera_state_from_screenshot, copy_image_metadata


def test_copy_image_metadata():
    metadata = {
        "foo": "bar baz",
        "hello": "world",
        "lorem": "ipsum",
    }
    img1 = f3d.Image(24, 12, 3, f3d.Image.ChannelType.BYTE)
    for k, v in metadata.items():
        img1.set_metadata(k, v)

    img2 = f3d.Image(8, 16, 1, f3d.Image.ChannelType.FLOAT)

    for k, v in metadata.items():
        assert img1.get_metadata(k) == v
        with raises(KeyError):
            img2.get_metadata(k)

    copy_image_metadata(img1, img2)

    for k, v in metadata.items():
        assert img2.get_metadata(k) == v


def test_camera_state_from_image():
    img = f3d.Image(24, 12, 3, f3d.Image.ChannelType.BYTE)
    img.set_metadata(
        "camera",
        "{"
        '  "position": [123, 456, 789],'
        '  "focalPoint": [12, 34, 56],'
        '  "viewUp": [0.1, 0.2, 0.3],'
        '  "viewAngle": 23'
        "}",
    )

    state = camera_state_from_screenshot(img)
    expected_state = f3d.CameraState((123, 456, 789), (12, 34, 56), (0.1, 0.2, 0.3), 23)

    assert state.position == expected_state.position
    assert state.focal_point == expected_state.focal_point
    assert state.view_up == expected_state.view_up
    assert state.view_angle == expected_state.view_angle


def test_camera_state_from_path():
    with NamedTemporaryFile(suffix=".png") as tmp:
        img = f3d.Image(24, 12, 3, f3d.Image.ChannelType.BYTE)
        img.set_metadata(
            "camera",
            "{"
            '  "position": [123, 456, 789],'
            '  "focalPoint": [12, 34, 56],'
            '  "viewUp": [0.1, 0.2, 0.3],'
            '  "viewAngle": 23'
            "}",
        )
        img.save(Path(tmp.name))

        state = camera_state_from_screenshot(tmp.name)
        expected_state = f3d.CameraState(
            (123, 456, 789), (12, 34, 56), (0.1, 0.2, 0.3), 23
        )

        assert state.position == expected_state.position
        assert state.focal_point == expected_state.focal_point
        assert state.view_up == expected_state.view_up
        assert state.view_angle == expected_state.view_angle


def test_camera_state_from_screenshot_no_metadata():
    img = f3d.Image(24, 12, 3, f3d.Image.ChannelType.BYTE)

    with raises(ValueError) as e:
        _ = camera_state_from_screenshot(img)
    assert "no camera metadata" in str(e)


@mark.parametrize(
    "json_metadata",
    [
        "{xxx",  # invalid json
        '{"position": 1}',  # invalid state,
        '{"position": [123, 456, 789]}',  # incomplete state
    ],
)
def test_camera_state_from_screenshot_invalid_metadata(json_metadata: str):
    img = f3d.Image(24, 12, 3, f3d.Image.ChannelType.BYTE)
    img.set_metadata("camera", json_metadata)

    with raises(ValueError) as e:
        _ = camera_state_from_screenshot(img)
    assert "invalid camera metadata" in str(e)
