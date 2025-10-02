import subprocess
from itertools import repeat
from tempfile import NamedTemporaryFile

import f3d
from pytest import mark

from f3d_extras.video import (
    ffmpeg_encode_sequence,
    ffmpeg_output_args_mp4,
    ffmpeg_output_args_webm,
    image_sequence_to_video,
)


def test_image_sequence_to_video():
    engine = f3d.Engine.create(offscreen=True)
    engine.window.size = 12, 34
    fps = 5
    duration = 2

    with NamedTemporaryFile(suffix=".mp4") as tmp:
        image_sequence_to_video(
            (engine.window.render_to_image() for _ in range(fps * duration)),
            fps,
            tmp.name,
        )

        ffprobe = subprocess.check_output(
            ["ffprobe", tmp.name], text=True, stderr=subprocess.STDOUT
        )
        w, h = engine.window.size
        assert f"{w}x{h}" in ffprobe
        assert f"Duration: 00:00:{duration:02d}" in ffprobe
        assert f"{fps} fps" in ffprobe


@mark.parametrize(
    "suffix, output_args, search",
    [
        (".mp4", ffmpeg_output_args_mp4(), "Video: h264"),
        (".webm", ffmpeg_output_args_webm(), "Video: vp9"),
    ],
)
def test_ffmpeg_encode_sequence(
    suffix: str, output_args: tuple[str | int, ...], search: str
):
    w, h = 12, 8
    fps = 5
    duration = 2
    with NamedTemporaryFile(suffix=suffix) as tmp:
        ffmpeg_encode_sequence(
            repeat(b"\0" * w * h * 3, fps * duration),
            (w, h),
            fps,
            tmp.name,
            output_args=output_args,
            vflip=True,
        )

        ffprobe = subprocess.check_output(
            ["ffprobe", tmp.name], text=True, stderr=subprocess.STDOUT
        )
        assert f"{w}x{h}" in ffprobe
        assert f"Duration: 00:00:{duration:02d}" in ffprobe
        assert f"{fps} fps" in ffprobe
        assert search in ffprobe
