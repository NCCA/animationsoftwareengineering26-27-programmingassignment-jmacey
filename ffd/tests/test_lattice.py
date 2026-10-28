from lattice import ControlPoint
import pytest
from ncca.ngl import Vec3


def test_control_point_constructor():
    cp = ControlPoint(Vec3(0,0,0))
    assert cp
    assert cp.pos == Vec3(0,0,0)
    assert not cp.selected 
