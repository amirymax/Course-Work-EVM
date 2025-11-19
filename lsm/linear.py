from typing import Sequence, Tuple
import numpy as np


def linear_least_squares(
    x_vals: Sequence[float],
    y_vals: Sequence[float],
) -> Tuple[float, float, float]:
    """
    Линейная аппроксимация y = a*x + b методом наименьших квадратов.

    :param x_vals: последовательность значений x_i
    :param y_vals: последовательность значений y_i
    :return: (a, b, S), где
             a, b - коэффициенты прямой,
             S    - сумма квадратов отклонений (ошибка аппроксимации)
    """
    x = np.asarray(x_vals, dtype=float)
    y = np.asarray(y_vals, dtype=float)

    if x.shape != y.shape:
        raise ValueError("x_vals и y_vals должны иметь одинаковую длину")

    # Матрица X: первый столбец единицы, второй — x
    X = np.column_stack((np.ones_like(x), x))

    # Решаем систему (X^T X) p = X^T y
    XtX = X.T @ X
    XtY = X.T @ y

    try:
        coeffs = np.linalg.solve(XtX, XtY)
    except np.linalg.LinAlgError:
        # На случай вырожденной системы
        return 0.0, 0.0, float("nan")

    b, a = coeffs  # порядок (b, a), см. p = [b, a]^T

    # Считаем сумму квадратов отклонений
    residuals = a * x + b - y
    S = float(np.sum(residuals ** 2))

    return float(a), float(b), S
