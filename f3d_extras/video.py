from itertools import chain
from pathlib import Path
import subprocess
from typing import Iterable, Iterator, Literal

import f3d


FfmpegLoglevelStr = Literal[
    "quiet", "panic", "fatal", "error", "warning", "info", "verbose", "debug", "trace"
]
FfmpegLoglevel = int | FfmpegLoglevelStr


def ffmpeg_output_args(*, crf: int = 8):
    """Basic `ffmpeg` arguments to encode `.mp4` videos."""
    return (
        *("-profile:v", "main"),
        *("-c:v", "libx264"),
        *("-pix_fmt", "yuv420p"),
        *("-crf", crf),
    )


def image_sequence_to_video(
    images: Iterable[f3d.Image],
    fps: float,
    out_path: Path | str,
    output_args: Iterable[str | int | float] = ffmpeg_output_args(),
    ffmpeg_executable: Path | str = "ffmpeg",
    loglevel: FfmpegLoglevel = "error",
):
    """Encode F3D images to video using `ffmpeg`."""

    def frames_and_resoultion() -> tuple[Iterable[bytes], tuple[int, int]]:
        it = iter(images)
        first = next(it)  # pop the first frame so we can check the resolution
        resolution = first.width, first.height
        raw_frames = (
            i.content  # raw bytes
            for i in chain([first], it)  # chain the first image back with the rest
        )
        return raw_frames, resolution

    ffmpeg_encode_sequence(
        *frames_and_resoultion(),
        fps=fps,
        out_path=out_path,
        output_args=output_args,
        vflip=True,
        pix_fmt="rgb24",
        loglevel=loglevel,
        ffmpeg_executable=ffmpeg_executable,
    )


def ffmpeg_encode_sequence(
    frames: Iterable[bytes],
    resolution: tuple[int, int],
    fps: float,
    out_path: Path | str,
    output_args: Iterable[str | int | float] = ffmpeg_output_args(),
    vflip: bool = False,
    pix_fmt: str = "rgb24",
    ffmpeg_executable: Path | str = "ffmpeg",
    loglevel: FfmpegLoglevel = "error",
):
    """Encode raw frames by piping to an `ffmpeg` subprocess."""

    def build_command() -> Iterator[str]:
        res = f"{resolution[0]}x{resolution[1]}"
        yield str(ffmpeg_executable)
        yield from ("-f", "rawvideo", "-pix_fmt", pix_fmt, "-s", res)
        yield from ("-r", f"{fps}", "-i", "-")
        if vflip:
            yield from ("-vf", "vflip")
        if output_args:
            yield from map(str, output_args)
        yield from ("-loglevel", str(loglevel))
        yield from (str(out_path), "-y")

    command = list(build_command())
    proc = subprocess.Popen(command, stdin=subprocess.PIPE)
    if stdin := proc.stdin:
        for frame in frames:
            stdin.write(frame)
            stdin.flush()
        stdin.close()
    proc.wait()
