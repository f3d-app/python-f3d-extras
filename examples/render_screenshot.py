import logging
from pathlib import Path
from tempfile import gettempdir

import f3d

from f3d_extras import download_file_if_url
from f3d_extras.images import camera_state_from_screenshot, copy_image_metadata


def main():
    screenshot_fn = Path(__file__).parent / "dragon_1.png"
    model_fn = "https://github.com/f3d-app/f3d/raw/refs/heads/master/testing/data/multi/dragon.vtu?download"
    options = {
        "render.effect.tone_mapping": True,
        "render.effect.ambient_occlusion": True,
        "render.effect.antialiasing.enable": True,
        "render.effect.antialiasing.mode": "ssaa",
        "scene.up_direction": "+y",
    }
    render_height = 1280

    render_fn = Path(gettempdir()) / screenshot_fn.name
    screenshot = f3d.Image(screenshot_fn)
    aspect_ratio = screenshot.width / screenshot.height

    engine = f3d.Engine.create(offscreen=True)
    engine.window.size = int(round(render_height * aspect_ratio)), render_height
    engine.options.update(options)
    engine.scene.add(download_file_if_url(model_fn))
    engine.window.camera.state = camera_state_from_screenshot(screenshot)

    render = engine.window.render_to_image(no_background=True)
    copy_image_metadata(screenshot, render)
    render.save(render_fn)
    print(f"rendered {render_fn} with the same camera as {screenshot_fn}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
