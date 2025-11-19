def chord(f, a, b, eps, max_iter=50):
    """
    Метод хорд (секущих).
    Возвращает найденный корень и число итераций.
    """
    # Проверка: на интервале должен быть корень
    if f(a) * f(b) >= 0:
        raise ValueError("На интервале нет смены знака функции.")

    n = 0
    bn_prev = b

    while True:
        # формула хорд
        bn = b - f(b) * (a - b) / (f(a) - f(b))
        n += 1

        if abs(bn - bn_prev) <= eps:
            return bn, n

        if n > max_iter:
            raise RuntimeError("Превышено максимальное число итераций.")

        bn_prev = bn
        b = bn
