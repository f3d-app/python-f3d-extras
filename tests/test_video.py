from itertools import repeat
import subprocess
from tempfile import NamedTemporaryFile

import f3d
from f3d_extras.video import ffmpeg_encode_sequence, image_sequence_to_video


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


def test_ffmpeg_encode_sequence():
    w, h = 12, 8
    fps = 5
    duration = 2
    with NamedTemporaryFile(suffix=".mp4") as tmp:
        ffmpeg_encode_sequence(
            repeat(b"\0" * w * h * 3, fps * duration),
            (w, h),
            fps,
            tmp.name,
            vflip=True,
        )

        ffprobe = subprocess.check_output(
            ["ffprobe", tmp.name], text=True, stderr=subprocess.STDOUT
        )
        assert f"{w}x{h}" in ffprobe
        assert f"Duration: 00:00:{duration:02d}" in ffprobe
        assert f"{fps} fps" in ffprobe
