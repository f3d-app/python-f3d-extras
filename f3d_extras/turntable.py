from math import cos, pi, sin
from typing import Any, Callable

import f3d
import numpy as np
from numpy.typing import NDArray


def turntable_interpolator(
    engine: f3d.Engine, *, turns: float = 1
) -> Callable[[float], None]:
    """Return a `t: float -> None` function that interpolates from `0 <= t <= 1`
    to spin the camera `turns` times around the engine's current focal point
    about its current `up_direction`."""

    state_interpolator = turntable_state_interpolator(
        initial_state=engine.window.camera.state,
        axis=engine.options["scene.up_direction"],  # type: ignore
        turns=turns,
    )

    def f(t: float):
        engine.window.camera.state = state_interpolator(t)

    return f


def turntable_state_interpolator(
    initial_state: f3d.CameraState,
    axis: tuple[float, float, float],
    *,
    turns: float = 1,
) -> Callable[[float], f3d.CameraState]:
    """Return a `t: float -> CameraState` function that interpolates from `0 <= t <= 1`
    to a camera state spinning `turns` times around `initial_state`'s focal point
    about the provided `axis`."""
    initial_foc = np.array(initial_state.focal_point, dtype=np.float64)
    initial_pos = np.array(initial_state.position, dtype=np.float64)
    initial_up = np.array(initial_state.view_up, dtype=np.float64)

    rotation = axis_rotation(axis, initial_foc)

    def interpolate_state(t: float):
        M = rotation(2 * pi * t * turns)
        foc = transform_point(M, initial_foc)
        pos = transform_point(M, initial_pos)
        up = transform_point(M, initial_pos + initial_up) - pos
        return f3d.CameraState(pos, foc, up, initial_state.view_angle)

    return interpolate_state


def axis_rotation(
    axis: tuple[float, float, float] | NDArray[np.floating[Any]],
    origin: tuple[float, float, float] | NDArray[np.floating[Any]] = (0, 0, 0),
):
    """Return an `angle: float -> matrix` function to compute 4x4 affine transform matrices
    using Rodrigues' rotation formula as described in https://mathworld.wolfram.com/RodriguesRotationFormula.html.
    """
    A = np.array(axis, np.float64) / np.linalg.norm(axis)
    M = np.array(
        [
            [0.0, -A[2], +A[1]],
            [+A[2], 0.0, -A[0]],
            [-A[1], +A[0], 0.0],
        ],
        np.float64,
    )
    MM = M @ M

    T = np.identity(4)
    T[:3, 3] = origin
    TI = np.linalg.inv(T)

    def f(angle: float):
        R = np.identity(4)
        R[:3, :3] += M * sin(angle) + MM * (1 - cos(angle))
        return T @ R @ TI

    return f


def transform_point(
    affine_4x4_matrix: NDArray[np.floating[Any]],
    point: tuple[float, float, float] | NDArray[np.floating[Any]],
):
    new_point = np.array([*point[:3], 1]) @ affine_4x4_matrix.T
    return new_point[:3] / new_point[3]
