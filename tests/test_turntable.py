from math import atan2, degrees
from typing import Sequence

import numpy as np
import pytest
from f3d import CameraState, Engine
from numpy import linspace
from numpy.typing import NDArray
from pytest import approx  # type: ignore

from f3d_extras.turntable import turntable_interpolator, turntable_state_interpolator

TEST_PARAMS = [
    # foc, pos, turns, axis, sample_count, expected_angles
    ((0, 0, 0), (1, 0, 0), 1, (0, 0, 1), 10, linspace(0, 360, 10)),
    ((1, 2, 3), (4, 3, 2), 2, (0, 1, 0), 12, linspace(0, 720, 12)),
    ((1, 2, 3), (10, 11, 12), -3, (3, 4, 5), 15, linspace(1080, 0, 15)),
]


@pytest.mark.parametrize(
    "foc, pos, turns, axis, sample_count, expected_angles", TEST_PARAMS
)
def test_turntable_camera_state_func(
    foc: tuple[float, float, float],
    pos: tuple[float, float, float],
    turns: float,
    axis: tuple[float, float, float],
    sample_count: int,
    expected_angles: Sequence[float],
):
    initial_state = CameraState()
    initial_state.focal_point = foc
    initial_state.position = pos
    f = turntable_state_interpolator(initial_state, axis, turns=turns)

    states = list(map(f, linspace(0, 1, sample_count)))

    assert all(
        approx(state.focal_point) == initial_state.focal_point for state in states
    )
    assert all(
        abs(turntable_angle(initial_state, state, axis) % 360 - angle % 360) % 360
        < 0.01
        for state, angle in zip(states, expected_angles)
    )


@pytest.mark.parametrize(
    "foc, pos, turns, axis, sample_count, expected_angles", TEST_PARAMS
)
def test_turntable_interpolator(
    foc: tuple[float, float, float],
    pos: tuple[float, float, float],
    turns: float,
    axis: tuple[float, float, float],
    sample_count: int,
    expected_angles: Sequence[float],
):
    engine = Engine.create(offscreen=True)
    engine.window.camera.focal_point = foc
    engine.window.camera.position = pos
    engine.options["scene.up_direction"] = list(axis)
    initial_state = engine.window.camera.state
    f = turntable_interpolator(engine, turns=turns)

    def collect_states():
        for t in linspace(0, 1, sample_count):
            f(t)
            yield engine.window.camera.state

    states = list(collect_states())

    assert all(approx(state.focal_point) == foc for state in states)
    assert all(
        abs(turntable_angle(initial_state, state, axis) % 360 - angle % 360) % 360
        < 0.01
        for state, angle in zip(states, expected_angles)
    )


def turntable_angle(
    state1: CameraState, state2: CameraState, axis: tuple[float, float, float]
):
    def proj(xyz: tuple[float, float, float]):
        p = np.array(xyz, dtype=np.float64)
        a = np.array(axis, dtype=np.float64)
        a /= np.linalg.norm(a)
        return p - a * np.dot(p, a)

    p0 = proj(state1.focal_point)
    p1 = proj(state1.position)
    p2 = proj(state2.position)
    return angle_between_vectors(p1 - p0, p2 - p0, ref=np.array(axis))


def angle_between_vectors(
    v1: NDArray[np.floating], v2: NDArray[np.floating], ref: NDArray[np.floating]
):
    cross = np.cross(v1, v2)
    angle = atan2(np.linalg.norm(cross), np.dot(v1, v2))
    return degrees(angle if np.dot(cross, ref) >= 0 else -angle)
