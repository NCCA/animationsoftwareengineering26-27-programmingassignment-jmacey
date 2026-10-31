import random

import pytest
from lattice import ControlPoint
from ncca.ngl import Vec3


@pytest.fixture
def cp():
    return ControlPoint(Vec3(0, 0, 0))


def test_control_point_constructor(cp):
    assert cp
    assert cp.pos == Vec3(0, 0, 0)
    assert not cp.selected


def test_control_point_toggle(cp):
    assert not cp.selected
    cp.toggle_selected()
    assert cp.selected


update_pos = [
    Vec3(),
    Vec3(0.1, 0.1, 0.1),
    Vec3(-1.0, 0, 0),
    Vec3(1, 0, 0),
    Vec3(0, -1, 0),
    Vec3(0, 1, 0),
    Vec3(0, 0, -1),
    Vec3(0, 0, 1),
]


@pytest.mark.parametrize("delta", (update_pos))
def test_move_control_point(cp, delta):
    assert cp.pos == Vec3(0, 0, 0)
    cp.move(delta)
    assert cp.pos == delta


original_pos = [Vec3(0, 0, 0), Vec3(2, 2, 2)]
delta = [Vec3(0.5, 0.2, 0.3), Vec3(-1, 0, 1)]
new_pos = [Vec3(0.5, 0.2, 0.3), Vec3(1, 2, 1)]
state = [False, True]


@pytest.mark.parametrize("original_pos,delta,new_pos,state", list(zip(original_pos, delta, new_pos, state)))
def test_cp_all(original_pos, delta, new_pos, state):
    cp = ControlPoint(original_pos)
    assert cp.pos == original_pos
    cp.move(delta)
    assert cp.pos == original_pos + delta
    if state:
        cp.toggle_selected()
    assert cp.selected == state


def test_bad_pos():
    with pytest.raises(ValueError):
        _ = ControlPoint(Vec3("a", "b", "c"))
    with pytest.raises(ValueError):
        _ = ControlPoint("hello")
