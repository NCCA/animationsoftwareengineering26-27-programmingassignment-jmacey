"""The main lattice and control point module for the FFD algorithm

This module contains the `ControlPoint` and `Lattice` classes

Typical usage will be that Lattice is constructed and uses the Control points.

Notes :
    Does CP need to be public? Lattice will create so perhaps could be private


"""

from math import comb

from ncca.ngl import Mat3, Vec3


class ControlPoint:
    """Single Control Point for the Lattice.
    Args :
        pos : initial position of the CP : Vec3

    Attributes :
        pos : Vec3 the current cp position
        selected : bool if the cp is active
    """

    def __init__(self, pos: Vec3):
        if not isinstance(pos, Vec3):
            raise ValueError("need Vec3 only")
        self._pos = pos
        self._selected = False

    @property
    def pos(self) -> Vec3:
        return self._pos

    @property
    def selected(self) -> bool:
        return self._selected

    def toggle_selected(self) -> None:
        """toggle if the control point is selected"""
        self._selected ^= True

    def move(self, delta: Vec3):
        self._pos += delta


class Lattice:
    """
    FFD control lattice of ControlPoints emebedded in a bounding box

    Args :
        shape : number of control points in s,t,u
        bbox_min the min corner of the Lattice : Vec3
        bbox_max the max corner of the lattice : Vec3
    """

    def __init__(self, shape: tuple[int, int, int], bbox_min: Vec3, bbox_max: Vec3):
        if len(shape) != 3 or any(int(n) < 2 for n in shape):
            raise ValueError("Lattice must have more than 2 control points in each direction")
        if not isinstance(bbox_min, Vec3) or not isinstance(bbox_max, Vec3):
            raise ValueError("Need Vec3 only")
        self._shape = shape
        self._origin = bbox_min.copy()
        extent = bbox_max - bbox_min
        # axis aligned edges used later for the actual maths
        self._s = Vec3(extent.x, 0.0, 0.0)
        self._t = Vec3(0.0, extent.y, 0.0)
        self._u = Vec3(0.0, 0.0, extent.z)
        self._volume = float(self._t.cross(self._u).dot(self._s))
        self._rest = self._build_grid()
        self._cvs = [ControlPoint(p.copy()) for p in self._rest]

    @property
    def shape(self) -> tuple[int, int, int]:
        return self._shape

    @property
    def cvs(self) -> tuple[ControlPoint, ...]:
        return tuple(self._cvs)

    @property
    def control_points(self) -> tuple[Vec3, ...]:
        return tuple(cp.pos for cp in self._cvs)

    @property
    def origin(self) -> Vec3:
        return self._origin

    @property
    def s(self) -> Vec3:
        return self._s

    @property
    def t(self) -> Vec3:
        return self._t

    @property
    def u(self) -> Vec3:
        return self._u

    @property
    def volume(self) -> float:
        return self._volume

    def _build_grid(self) -> list[Vec3]:
        """
        Evenly spaced points X0  + i/(l-1)S + j/(m-1) T + k/(n-1) U
        """
        l, m, n = self._shape
        return [
            self._origin + self._s * (i / (l - 1)) + self._t * (j / (m - 1)) + self._u * (k / (n - 1))
            for i in range(l)
            for j in range(m)
            for k in range(n)
        ]

    def __len__(self) -> int:
        return len(self._cvs)

    def index(self, i: int, j: int, k: int) -> int:
        """Convert (i,j,k) lattice cords into flat list index"""
        l, m, n = self._shape
        if not (0 <= i < l and 0 <= j < m and 0 <= k < n):
            raise IndexError(f"({i},{j},{k}) outside lattice of shape {self._shape}")
        return (i * m + j) * n + k

    def __getitem__(self, ijk: tuple[int, int, int]) -> ControlPoint:
        return self._cvs[self.index(*ijk)]

    def __iter__(self):
        return iter(self._cvs)

    @property
    def selected(self) -> list[ControlPoints]:
        return [cp for cp in self._cvs if cp.selected]

    def select_all(self):
        for cp in self._cvs:
            if not cp.selected:
                cp.toggle_selected()

    def deselect_all(self):
        for cp in self._cvs:
            if cp.selected:
                cp.toggle_selected()

    def edges(self) -> list[int, int]:
        l, m, n = self._shape
        edges = []
        for i in range(l):
            for j in range(m):
                for k in range(n):
                    if i + 1 < l:
                        edges.append((self.index(i, j, k), self.index(i + 1, j, k)))
                    if j + 1 < m:
                        edges.append((self.index(i, j, k), self.index(i, j + 1, k)))
                    if k + 1 < n:
                        edges.append((self.index(i, j, k), self.index(i, j, k + 1)))

        return edges
