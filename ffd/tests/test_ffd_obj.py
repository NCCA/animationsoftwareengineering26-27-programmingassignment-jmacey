from pathlib import Path

import pytest
from ffd_obj import FFDObj
from ncca.ngl import Vec3

TEST_DIR = Path(__file__).resolve().parent


def test_contruct():
    obj = FFDObj(f"{TEST_DIR}/unit_cube.obj")
    assert obj
    assert obj.bbox_min == Vec3(-0.5, -0.5, -0.5)
    assert obj.bbox_max == Vec3(0.5, 0.5, 0.5)
