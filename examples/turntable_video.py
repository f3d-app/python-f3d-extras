import logging
from pathlib import Path
from tempfile import gettempdir
from typing import Any

import f3d
from tqdm import tqdm

from f3d_extras import (
    download_file_if_url,
    ffmpeg_output_args,
    image_sequence_to_video,
    turntable_state_interpolator,
)


def main():
    resolution = 1280, 720
    initial_camera_position = 1, 1, 1
    camera_zoom_factor = 1.2
    duration = 5
    fps = 30
    turns = 1
    model_fn = "https://github.com/KhronosGroup/glTF-Sample-Models/raw/main/2.0/DamagedHelmet/glTF-Binary/DamagedHelmet.glb"
    hdri_fn = "https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/2k/industrial_sunset_02_puresky_2k.hdr"
    video_path = Path(gettempdir()) / "f3d-turntable.mp4"

    options: dict[str, Any] = {
        "render.hdri.ambient": "on",
        "render.background.skybox": True,
        "render.background.blur.enable": True,
        "render.hdri.file": str(download_file_if_url(hdri_fn)),
        "render.effect.translucency_support": True,
        "render.effect.tone_mapping": True,
        "render.effect.ambient_occlusion": True,
        "render.effect.antialiasing.enable": True,
        "scene.up_direction": "+y",
        "ui.axis": True,
        "render.grid.enable": True,
    }

    engine = f3d.Engine.create(offscreen=False)
    engine.window.size = resolution
    engine.options.update(options)

    engine.scene.add(download_file_if_url(model_fn))
    engine.window.camera.position = initial_camera_position
    engine.window.camera.reset_to_bounds(zoom_factor=camera_zoom_factor)

    camera_state_interpolator = turntable_state_interpolator(
        engine.window.camera.state,
        engine.options["scene.up_direction"],  # type: ignore
        turns=turns,
    )

    def render_images():
        t = 0.0
        while t < duration:
            engine.window.camera.state = camera_state_interpolator(float(t) / duration)
            yield engine.window.render_to_image()
            t += 1.0 / fps

    image_sequence_to_video(
        tqdm(render_images(), total=fps * duration),  # tqdm for progress bar
        fps,
        video_path,
        output_args=ffmpeg_output_args(
            crf=8,  # lower => higher quality
        ),
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
