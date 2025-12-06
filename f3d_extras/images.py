import json
from pathlib import Path

import f3d


def copy_image_metadata(src: f3d.Image, dst: f3d.Image):
    """Copy all of `f3d`'s metadata from one image to the other."""
    for key in src.all_metadata():
        dst.set_metadata(key, src.get_metadata(key))


def camera_state_from_screenshot(screenshot: f3d.Image | Path | str):
    """Retrieve the camera state from a screenshot saved from the F3D application."""

    image = (
        screenshot if isinstance(screenshot, f3d.Image) else f3d.Image(Path(screenshot))
    )

    try:
        cam_metadata_json_str = image.get_metadata("camera")
    except KeyError:
        raise ValueError(f"no camera metadata in {screenshot}")

    try:
        cam_metadata = json.loads(cam_metadata_json_str)
        return f3d.CameraState(
            cam_metadata["position"],
            cam_metadata["focalPoint"],
            cam_metadata["viewUp"],
            cam_metadata["viewAngle"],
        )
    except (KeyError, ValueError):
        raise ValueError(f"invalid camera metadata in {screenshot}")
