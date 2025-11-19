def dichotomy(f, a, b, eps):
    """
    Метод дихотомии (бисекции).
    Возвращает найденный корень и количество итераций.
    """
    n = 0

    while True:
        c = (a + b) / 2
        fc = f(c)

        if abs(fc) < eps:     # критерий остановки
            return c, n + 1

        if f(a) * fc < 0:
            b = c
        else:
            a = c

        n += 1
