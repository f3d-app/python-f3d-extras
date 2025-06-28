import logging
import time
from colorsys import hsv_to_rgb
from math import sin
from typing import Any

import f3d

from f3d_extras import download_file_if_url


def main():
    model_fn = "https://lazarsoft.info/objstl/teddy.obj"

    options: dict[str, Any] = {
        "render.effect.tone_mapping": True,
        "render.effect.ambient_occlusion": True,
        "render.effect.antialiasing.enable": True,
        "scene.up_direction": "+y",
        "ui.axis": True,
        "render.grid.enable": True,
        "render.show_edges": True,
    }

    engine = f3d.Engine.create()
    engine.window.size = 900, 720
    engine.options.update(options)

    engine.scene.add(download_file_if_url(model_fn))
    engine.window.camera.position = 1, 1, 1
    engine.window.camera.reset_to_bounds(zoom_factor=1.2)

    t0 = time.time()

    def on_every_frame():
        t = time.time() - t0
        u = sum(1 + sin(t * f) for f in (3, 4, 5)) / 6
        engine.options["render.line_width"] = u * 15
        engine.options["model.color.rgb"] = hsv_to_rgb(u, 0.5, 0.5)
        engine.options["render.grid.color"] = hsv_to_rgb(u + 0.5, 0.5, 0.5)
        engine.options["render.background.color"] = hsv_to_rgb(u + 0.5, 0.2, 0.2)
        engine.options["render.grid.unit"] = 10 + u * 50
        engine.interactor.request_render()

        if t > 30:  # stop after 10s
            engine.interactor.stop()

    engine.interactor.start(1 / 30, on_every_frame)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
