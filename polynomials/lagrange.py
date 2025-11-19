def lagrange(x_eval: float, xs: list, ys: list) -> float:
    """
    Интерполяция полиномом Лагранжа.
    xs, ys — списки узлов (одной длины)
    x_eval — точка, в которой нужно найти значение P(x)
    """
    n = len(xs)
    result = 0.0

    for i in range(n):
        term = ys[i]
        for j in range(n):
            if j != i:
                term *= (x_eval - xs[j]) / (xs[i] - xs[j])
        result += term

    return result


# пример использования
# xs = [-1, -0.5, 0, 0.5, 1.0, 1.5]
# ys = [-2, 0, 1, 3.5, 4, 3.5]

# value = lagrange(0.1, xs, ys)
# print("P_Lagrange(0.1) =", value)
