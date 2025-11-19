def iteration_method(fi, x0, eps, max_iter=50):
    """
    Простой итерационный метод.
    fi — функция φ(x), преобразованная заранее.
    """
    x = x0
    n = 0

    while True:
        xn = fi(x)
        dx = abs(xn - x)
        n += 1

        if n > max_iter:
            raise RuntimeError("Итераций > 50, метод расходится")

        if dx <= eps:
            return xn, n

        x = xn
