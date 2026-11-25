import pytest
from colour_generator import _ColourGenerator


@pytest.fixture
def gen() -> _ColourGenerator:
    return _ColourGenerator()


def test_background_default(gen: _ColourGenerator):
    assert gen.background == (0, 0, 0)
    gen.background = (255, 0, 0)
    assert gen.background == (255, 0, 0)


def test_reserve(gen: _ColourGenerator):
    gen.reserve((1, 0, 0))
    colour = gen.get_next_colour_id()
    assert colour == (2, 0, 0)
    colour = gen.get_next_colour_id()
    assert colour == (3, 0, 0)
