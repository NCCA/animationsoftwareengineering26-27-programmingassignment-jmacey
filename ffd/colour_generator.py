from collections.abc import Iterator
from threading import Lock
from typing import TypeAlias

RGB: TypeAlias = tuple[int, int, int]


class _ColourGenerator:
    """Allocate unique 24-bit RGB picking colours"""

    def __init__(self) -> None:
        self._reserved: set[RGB] = set()
        self._background: RGB = (0, 0, 0)
        self._lock = Lock()
        self._next_colour: Iterator[RGB] = self._colour_id_generator()

    @property
    def background(self) -> RGB:
        return self._background

    @background.setter
    def background(self, colour: RGB) -> None:
        """set the background colour"""
        with self._lock:
            self._background = colour

    @staticmethod
    def _colour_id_generator() -> Iterator[RGB]:
        """Yield RGB picking IDS from 1 - 2**24-1"""
        for colour_id in range(1, 1 << 24):
            yield (colour_id & 0xFF, (colour_id >> 8) & 0xFF, (colour_id >> 16) & 0xFF)

    def reserve(self, *colours: RGB) -> None:
        """exclude these colours from future allocations ideal for adding
        manipulator colours for selection later"""
        with self._lock:
            self._reserved.update(colours)

    def _generate(self) -> Iterator[RGB]:
        """yield next colour from current position excluding bg and reserved"""
        while True:
            with self._lock:
                colour = next(self._next_colour, None)
                if colour is None:
                    return
                if colour == self._background or colour in self._reserved:
                    continue
            yield colour

    def get_next_colour_id(self) -> RGB:
        colour = self._generate()
        return next(colour)


colour_generator = _ColourGenerator()
