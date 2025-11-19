import numpy as np

def matrix_method(xs: list, ys: list):
    """
    Решение системы A*p = Y матричным способом.
    Возвращает коэффициенты полинома.
    """
    xs = np.array(xs, dtype=float)
    ys = np.array(ys, dtype=float)

    n = len(xs)

    # Матрица Вандермонда A
    A = np.vander(xs, N=n, increasing=True)

    # Обратная матрица A^{-1}
    A_inv = np.linalg.inv(A)

    # Умножение A^{-1} * Y
    coeffs = np.dot(A_inv, ys)

    return coeffs


def eval_poly(coeffs, x):
    """Вычисление полинома по найденным коэффициентам."""
    return sum(coeffs[i] * x**i for i in range(len(coeffs)))


# Пример
# xs = [-1, -0.5, 0, 0.5, 1.0, 1.5]
# ys = [-2, 0, 1, 3.5, 4, 3.5]

# coeffs = matrix_method(xs, ys)
# value = eval_poly(coeffs, 0.1)

# print("Коэффициенты:", coeffs)
# print("P(0.1) =", value)
