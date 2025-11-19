def newton_interpolation(x, xs, ys):
    """
    Интерполяция методом Ньютона с использованием таблицы конечных разностей.
    xs — массив узлов x
    ys — массив значений y
    x  — точка, в которой нужно вычислить P(x)
    """
    import math

    n = len(xs)

    # Таблица конечных разностей
    diff = [[0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        diff[i][0] = ys[i]

    # Вычисляем конечные разности всех порядков
    for j in range(1, n):
        for i in range(n - j):
            diff[i][j] = diff[i + 1][j - 1] - diff[i][j - 1]

    # Шаг таблицы
    h = xs[1] - xs[0]
    t = (x - xs[0]) / h

    # Вычисляем значение полинома
    result = diff[0][0]
    t_prod = 1

    for j in range(1, n):
        t_prod *= (t - (j - 1))
        result += t_prod * diff[0][j] / math.factorial(j)

    return result
