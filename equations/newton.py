def newton(f, fp, x0, eps, max_iter=50):
    """
    Метод Ньютона (касательных).
    Возвращает найденный корень и число итераций.
    """
    n = 0
    x = x0

    while True:
        if fp(x) == 0:
            raise ZeroDivisionError(
                "Производная равна 0. Требуется другое начальное приближение."
            )

        x_new = x - f(x) / fp(x)
        n += 1

        if abs(x_new - x) <= eps:
            return x_new, n

        if n > max_iter:
            raise RuntimeError("Количество итераций превысило допустимый предел")

        x = x_new
