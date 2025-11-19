import numpy as np

def canonical_polynomial(x_eval: float, xs: list, ys: list) -> float:
    """
    Вычисление интерполяционного полинома в канонической форме.
    xs — точки X
    ys — точки Y
    x_eval — точка, в которой нужно вычислить P(x)
    """

    xs = np.array(xs, dtype=float)
    ys = np.array(ys, dtype=float)

    n = len(xs)

    # Формирование матрицы Вандермонда
    A = np.vander(xs, N=n, increasing=True)

    # Решение системы A * coeffs = ys
    coeffs = np.linalg.solve(A, ys)

    # Вычисление значения полинома
    x_powers = np.array([x_eval ** i for i in range(n)])
    result = np.dot(coeffs, x_powers)

    return result


# Пример использования:
# xs = [-1, -0.5, 0, 0.5, 1.0, 1.5]
# ys = [-2, 0, 1, 3.5, 4, 3.5]

# value = canonical_polynomial(0.1, xs, ys)
# print("P(0.1) =", value)
