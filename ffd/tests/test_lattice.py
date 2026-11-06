import random

import pytest
from lattice import ControlPoint, Lattice
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


@pytest.mark.parametrize(
    "original_pos,delta,new_pos,state", list(zip(original_pos, delta, new_pos, state, strict=False))
)
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


@pytest.fixture
def lattice():
    return Lattice((2, 2, 2), Vec3(0, 0, 0), Vec3(1, 1, 1))


def test_lattice_construct():
    lattice = Lattice((2, 2, 2), Vec3(-1, -1, -1), Vec3(1, 1, 1))
    assert lattice
    assert lattice.shape == (2, 2, 2)
    assert lattice.origin == Vec3(-1, -1, -1)
    assert lattice.s == Vec3(2.0, 0.0, 0.0)
    assert lattice.t == Vec3(0.0, 2.0, 0.0)
    assert lattice.u == Vec3(0.0, 0.0, 2.0)
    assert lattice.volume == pytest.approx(8)
    # assert lattice.cvs is not None
    assert lattice._rest is not None
    rest = lattice._rest
    assert len(rest) == 2 * 2 * 2
    assert len(lattice)
    for i in range(2):
        for j in range(2):
            for k in range(2):
                assert lattice[i, j, k]
                assert isinstance(lattice[i, j, k], ControlPoint)
    for cv in lattice:
        assert isinstance(cv, ControlPoint)

    assert len(lattice.selected) == 0


# this generate all combinations of u,v,w from 0-2 excluding 2,2,2 which is valid (hence the [:-1])
@pytest.mark.parametrize("u,v,w", [(u, v, w) for u in range(0, 3) for v in range(0, 3) for w in range(0, 3)][:-1])
def test_lattice_shape_error(u, v, w):
    with pytest.raises(ValueError):
        _ = Lattice((u, v, w), Vec3(-1, -1, -1), Vec3(1, 1, 1))

    for i in range(0, 3):
        input = [3] * i
        with pytest.raises(ValueError):
            _ = Lattice(input, Vec3(-1, -1, -1), Vec3(1, 1, 1))


def test_lattice_bbox_error():
    with pytest.raises(ValueError):
        Lattice((2, 2, 2), int(), Vec3(1, 1, 1))
    with pytest.raises(ValueError):
        Lattice((2, 2, 2), int(), float())


def test_rest_extent(lattice):
    print(lattice._rest)


def test_selection_toggle(lattice):
    assert len(lattice.selected) == 0
    lattice.select_all()
    assert len(lattice.selected) == 8
    lattice.deselect_all()
    assert len(lattice.selected) == 0
    lattice[0, 0, 0].toggle_selected()
    assert len(lattice.selected) == 1
    lattice[0, 0, 0].toggle_selected()
    assert len(lattice.selected) == 0
