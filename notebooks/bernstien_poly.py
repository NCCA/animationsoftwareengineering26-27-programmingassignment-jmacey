import marimo

__generated_with = "0.25.2"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    from math import comb
    import matplotlib.pyplot as plt

    return comb, mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Bernstein Polynomials and Free Form Deformation

    ## Bernstein polynomials

    The Bernstein basis polynomials of degree $n$ are defined as

    $$
    B_{i,n}(t) = \binom{n}{i} t^i (1-t)^{n-i}, \quad i = 0 \ldots n, \quad t \in [0,1]
    $$

    where $\binom{n}{i} = \frac{n!}{i!(n-i)!}$ is the binomial coefficient. For a given degree there are $n+1$ of them, for example the cubic ($n=3$) set is

    $$
    B_{0,3} = (1-t)^3, \quad B_{1,3} = 3t(1-t)^2, \quad B_{2,3} = 3t^2(1-t), \quad B_{3,3} = t^3
    $$

    If you have used Bézier curves you have already met these, a Bézier curve is just a set of control points blended together using the Bernstein polynomials as weights

    $$
    C(t) = \sum_{i=0}^{n} B_{i,n}(t) \, P_i
    $$
    """)
    return


@app.cell
def _(comb, np):
    def bernstein(degree: int, t: np.ndarray) -> np.ndarray:
        """
        Evaluate all the Bernstein basis polynomials of a given degree for an array of t values.

        Parameters
        ----------
            degree : int
                the polynomial degree (lattice divisions - 1)
            t : np.ndarray
                shape (N,) parameter values in the range [0,1]

        Returns
        -------
            np.ndarray
                shape (N, degree + 1) where column i is C(degree, i) * (1-t)^(degree-i) * t^i
        """
        if degree < 0:
            raise ValueError(f"degree must be >= 0, got {degree}")
        t = np.asarray(t, dtype=np.float64).reshape(-1, 1)
        i = np.arange(degree + 1)
        coefficients = np.array([comb(degree, k) for k in i], dtype=np.float64)
        # numpy defines 0**0 as 1 so the end points t=0 and t=1 are handled without special cases
        return coefficients * (1.0 - t) ** (degree - i) * t**i

    return (bernstein,)


@app.cell
def _(mo, np):
    values = np.linspace(0, 1.0, 200)

    degree = mo.ui.slider(
        start=1, stop=20, value=3, step=1, label="slider", show_value=True
    )
    degree
    return degree, values


@app.cell
def _(bernstein, degree, plt, values):
    coefficients = bernstein(degree.value, values)

    fig, ax = plt.subplots(figsize=(7, 4), layout="constrained")
    ax.plot(
        values,
        coefficients,
        label=[f"B{i},{degree.value}" for i in range(degree.value + 1)],
    )
    ax.plot(values, coefficients.sum(axis=1), "k--", label="sum")
    ax.set_xlabel("t")
    ax.set_ylabel("weight")
    ax.set_title(f"Bernstein basis, degree {degree.value}")
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5))
    plt.close(fig)
    fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    There are a few properties that make them useful for us (try the slider above to see them)

    - **Partition of unity** : for any $t$ the weights sum to 1, $\sum_i B_{i,n}(t) = 1$ (the dashed line in the plot).
    - **Non-negative** : every $B_{i,n}(t) \geq 0$ on $[0,1]$ so the result is always a weighted average of the control points (it stays inside their convex hull).
    - **End point interpolation** : at $t=0$ only $B_{0,n}$ is non-zero and at $t=1$ only $B_{n,n}$, so the curve passes through the first and last points.
    - **Symmetry** : $B_{i,n}(t) = B_{n-i,n}(1-t)$.
    - **Single peak** : each $B_{i,n}$ has its maximum at $t = i/n$, so each control point has most influence near "its" position along the curve.
    - **Linear precision** : if the control points are evenly spaced along a line, $C(t)$ gives back exactly the point at $t$ along that line. This is the important one for FFD.

    ## From curves to volumes

    Free Form Deformation (FFD) was introduced by [Sederberg and Parry](https://dl.acm.org/doi/10.1145/15886.15903) at SIGGRAPH 1986. The idea is to embed an object inside a lattice of control points, then deform the lattice and let the object follow.

    Rather than one parameter $t$ we now have three $(s, t, u)$, one for each axis of the lattice. The deformation is a trivariate tensor product Bernstein polynomial (a Bézier volume)

    $$
    X_{ffd}(s,t,u) = \sum_{i=0}^{l} \sum_{j=0}^{m} \sum_{k=0}^{n} B_{i,l}(s) \, B_{j,m}(t) \, B_{k,n}(u) \, P_{ijk}
    $$

    where the lattice has $(l+1) \times (m+1) \times (n+1)$ control points $P_{ijk}$. Note in the code `dims` is the number of points, so the degree passed to `bernstein` is `dims - 1`.

    ### Embedding the object

    Before we can deform anything each vertex $X$ needs its local $(s,t,u)$ co-ordinates. With the lattice origin $X_0$ and edge vectors $S$, $T$ and $U$, any point in the lattice can be written as

    $$
    X = X_0 + sS + tT + uU
    $$

    so we need to solve this for $s$, $t$ and $u$. The trick is to take the dot product of both sides with a vector perpendicular to two of the edges, which makes those two terms vanish. $T \times U$ is perpendicular to both $T$ and $U$, so $(T \times U) \cdot T = 0$ and $(T \times U) \cdot U = 0$, giving

    $$
    (T \times U) \cdot (X - X_0) = s \, (T \times U) \cdot S
    \quad \Rightarrow \quad
    s = \frac{(T \times U) \cdot (X - X_0)}{(T \times U) \cdot S}
    $$

    Doing the same with $U \times S$ (perpendicular to $U$ and $S$) and $S \times T$ (perpendicular to $S$ and $T$) gives

    $$
    t = \frac{(U \times S) \cdot (X - X_0)}{(U \times S) \cdot T}, \quad
    u = \frac{(S \times T) \cdot (X - X_0)}{(S \times T) \cdot U}
    $$

    #### Why the order of the cross product matters

    The original paper (and quite a few notes based on it) has errors in these equations, so it is worth knowing how to check them rather than copying them.

    - The cross product is anti-commutative, $A \times B = -(B \times A)$. Swapping the order in **both** the numerator and denominator is harmless as the minus signs cancel. Swapping it in only one of them flips the sign and every co-ordinate comes out in $[-1, 0]$ rather than $[0, 1]$.
    - Keeping the cyclic order $S \to T \to U$ ($T \times U$, $U \times S$, $S \times T$) means all three denominators are the same value, the scalar triple product
      $$
      (T \times U) \cdot S = (U \times S) \cdot T = (S \times T) \cdot U = \det[\,S \; T \; U\,]
      $$
      which is the volume of the lattice. So it only needs calculating once and it is positive for a right handed lattice.
    - If that volume is zero the edge vectors are coplanar (for example a flat plane mesh with no thickness) and the division fails. The bounding box needs padding in this case.
    - This is really just [Cramer's rule](https://en.wikipedia.org/wiki/Cramer%27s_rule) for the $3 \times 3$ system $[\,S \; T \; U\,] \, (s,t,u)^T = X - X_0$, so `np.linalg.solve` would give the same answer.

    A simple sanity check is $X = X_0$ which must give $(0,0,0)$, and $X = X_0 + S + T + U$ which must give $(1,1,1)$.

    For an axis aligned bounding box this all collapses to $(X - X_0) / \text{extent}$ per axis, but keeping the general form means skewed or rotated lattices still work.
    ### Limitations

    Bernstein polynomials have **global support** : every control point influences every vertex (only a tiny amount for distant ones, but never zero). Adding more lattice points also raises the polynomial degree, so a dense lattice gives smoother but less local control and gets more expensive to evaluate. Later work replaced the Bernstein basis with B-splines to get local control, see [Extended FFD](https://dl.acm.org/doi/10.1145/97879.97900) (Coquillart 1990) and [MacCracken and Joy](https://dl.acm.org/doi/10.1145/237170.237247) (1996).
    """)
    return


if __name__ == "__main__":
    app.run()
