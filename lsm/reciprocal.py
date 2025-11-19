import numpy as np
from typing import Sequence, Tuple


def reciprocal_least_squares(
    x_vals: Sequence[float],
    y_vals: Sequence[float],
) -> Tuple[float, float, float]:
    """
    МНК для функции вида y = a/x + b.
    Возвращает (a, b, сумма_квадратов_ошибок)
    """
    x = np.asarray(x_vals, dtype=float)
    y = np.asarray(y_vals, dtype=float)

    if np.any(x == 0):
        raise ValueError("Значения x не должны быть равны нулю.")

    z = 1 / x  # преобразование

    # Матрица для линейной аппроксимации
    X = np.column_stack((z, np.ones_like(z)))

    # Решаем систему МНК
    coeffs = np.linalg.lstsq(X, y, rcond=None)[0]
    a, b = coeffs

    # Ошибка аппроксимации
    y_pred = a / x + b
    S = float(np.sum((y_pred - y) ** 2))

    return float(a), float(b), S
