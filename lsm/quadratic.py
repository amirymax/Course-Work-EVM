from typing import Sequence, Tuple
import numpy as np


def quadratic_least_squares(
    x_vals: Sequence[float],
    y_vals: Sequence[float],
) -> Tuple[float, float, float, float]:
    """
    Квадратичная аппроксимация y = a*x^2 + b*x + c методом наименьших квадратов.

    :param x_vals: последовательность значений x_i
    :param y_vals: последовательность значений y_i
    :return: (a, b, c, S), где
             a, b, c - коэффициенты квадратичной функции,
             S       - сумма квадратов отклонений
    """
    x = np.asarray(x_vals, dtype=float)
    y = np.asarray(y_vals, dtype=float)

    if x.shape != y.shape:
        raise ValueError("x_vals и y_vals должны иметь одинаковую длину")

    # Матрица X: [1, x, x^2]
    X = np.column_stack((np.ones_like(x), x, x**2))

    XtX = X.T @ X
    XtY = X.T @ y

    try:
        coeffs = np.linalg.solve(XtX, XtY)
    except np.linalg.LinAlgError:
        # Вырожденная система
        return 0.0, 0.0, 0.0, float("nan")

    c, b, a = coeffs  # порядок (c, b, a) как в p

    # Сумма квадратов отклонений
    y_pred = a * x**2 + b * x + c
    residuals = y_pred - y
    S = float(np.sum(residuals**2))

    return float(a), float(b), float(c), S
