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
        start=1, stop=10, value=3, step=5, label="slider", show_value=True
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


if __name__ == "__main__":
    app.run()
