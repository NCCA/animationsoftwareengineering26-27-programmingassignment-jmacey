"""Bernstein basis polynomials used to blend the lattice control points.

This is the simple pure python version, one t value at a time. The notebook in
notebooks/bernstien_poly.py has a numpy version that works on arrays of t.
"""

from math import comb


def bernstein(degree: int, t: float) -> list[float]:
    """
    Evaluate all the Bernstein basis polynomials of a given degree at t.

    Parameters
    ----------
        degree : int
            the polynomial degree, for a lattice this is the number of control points - 1
        t : float
            parameter value in the range [0,1]

    Returns
    -------
        list[float]
            degree + 1 values where element i is C(degree, i) * (1-t)^(degree-i) * t^i
    """
    if degree < 0:
        raise ValueError(f"degree must be >= 0, got {degree}")
    # Vec3 components are numpy float32 and Vec3 * scalar only accepts a python float
    t = float(t)
    # python defines 0**0 as 1 so t=0 and t=1 need no special cases
    return [comb(degree, i) * (1.0 - t) ** (degree - i) * t**i for i in range(degree + 1)]
