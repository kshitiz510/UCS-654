import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


ROLL_NUMBER = 102303748
DATA_FILE = "india-air-quality-data.csv"


def transform_values(values, roll):
    a = 0.05 * (roll % 7)
    b = 0.3 * ((roll % 5) + 1)
    return values + a * np.sin(b * values)


def gaussian_like(x, lam, mu, scale):
    return scale * np.exp(-lam * (x - mu) ** 2)


def empirical_density(data, bins=80):
    density, edges = np.histogram(data, bins=bins, density=True)
    centers = 0.5 * (edges[:-1] + edges[1:])
    return centers, density


def fit_parameters(x_vals, y_vals, data):
    start = [
        1 / (2 * np.var(data)),
        np.mean(data),
        np.max(y_vals)
    ]
    params, _ = curve_fit(gaussian_like, x_vals, y_vals, p0=start)
    return params


def main():
    df = pd.read_csv(DATA_FILE, encoding="latin1")
    no2_series = pd.to_numeric(df["no2"], errors="coerce").dropna()

    z = transform_values(no2_series.to_numpy(), ROLL_NUMBER)

    x_emp, y_emp = empirical_density(z)
    lam, mu, c = fit_parameters(x_emp, y_emp, z)

    print("lambda =", lam)
    print("mu =", mu)
    print("c =", c)

    plt.figure(figsize=(8, 4))
    plt.bar(x_emp, y_emp, width=(x_emp[1] - x_emp[0]), alpha=0.5)

    grid = np.linspace(z.min(), z.max(), 500)
    plt.plot(grid, gaussian_like(grid, lam, mu, c), color="red", linewidth=2)

    plt.xlabel("z")
    plt.ylabel("Density")
    plt.tight_layout()
    plt.savefig("fitted.png", dpi=300)
    plt.show()


if __name__ == "__main__":
    main()
