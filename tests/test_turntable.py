from math import atan2, degrees
from typing import Sequence

import numpy as np
import pytest
from f3d import CameraState
from numpy import linspace
from numpy.typing import NDArray
from pytest import approx  # type: ignore

from f3d_extras.turntable import turntable_state_interpolator


@pytest.mark.parametrize(
    "foc, pos, turns, axis, sample_count, expected_angles",
    [
        ((0, 0, 0), (1, 0, 0), 1, (0, 0, 1), 10, linspace(0, 360, 10)),
        ((1, 2, 3), (4, 3, 2), 2, (0, 1, 0), 12, linspace(0, 720, 12)),
        ((1, 2, 3), (10, 11, 12), -3, (3, 4, 5), 15, linspace(1080, 0, 15)),
    ],
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

    def proj(xyz: tuple[float, float, float]):
        p = np.array(xyz, dtype=np.float64)
        a = np.array(axis, dtype=np.float64)
        a /= np.linalg.norm(a)
        return p - a * np.dot(p, a)

    def check_angle(state: CameraState):
        p0 = proj(initial_state.focal_point)
        p1 = proj(initial_state.position)
        p2 = proj(state.position)
        return angle_between_vectors(p1 - p0, p2 - p0, ref=np.array(axis))

    states = list(map(f, linspace(0, 1, sample_count)))

    assert all(
        approx(state.focal_point) == initial_state.focal_point for state in states
    )
    assert all(
        abs(check_angle(state) % 360 - angle % 360) % 360 < 0.01
        for state, angle in zip(states, expected_angles)
    )


def angle_between_vectors(
    v1: NDArray[np.floating], v2: NDArray[np.floating], ref: NDArray[np.floating]
):
    cross = np.cross(v1, v2)
    angle = atan2(np.linalg.norm(cross), np.dot(v1, v2))
    return degrees(angle if np.dot(cross, ref) >= 0 else -angle)
