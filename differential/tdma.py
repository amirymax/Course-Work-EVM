def tdma(mtx, rhs, eps: float = 1e-15):
    """
    Решение трёхдиагональной СЛАУ методом прогонки (TDMA).

    mtx – список коэффициентов [(a1, b1, c1), (a2, b2, c2), ..., (aN, bN, cN)]
          a_i – поддиагональ, b_i – главная диагональ, c_i – наддиагональ
    rhs – список правых частей [f1, f2, ..., fN]

    Возвращает список значений y[0..N+1].
    y[0] и y[N+1] обычно задаются граничными условиями (мы их не трогаем),
    а y[1..N] вычисляются методом прогонки.
    """
    n = len(rhs)
    if n == 0:
        return []

    # Разворачиваем mtx в отдельные массивы a, b, c
    a = [0.0] * n
    b = [0.0] * n
    c = [0.0] * n
    f = [0.0] * n

    for i in range(n):
        a[i], b[i], c[i] = mtx[i]
        f[i] = rhs[i]

    # Прямой ход: коэффициенты α_i (cp) и β_i (fp)
    cp = [0.0] * n   # аналог cp()
    fp = [0.0] * n   # аналог fp()

    if abs(b[0]) < eps:
        raise ZeroDivisionError("TDMA: division by zero on first step")

    cp[0] = c[0] / b[0]
    fp[0] = f[0] / b[0]

    for i in range(1, n):
        m = b[i] - a[i] * cp[i - 1]
        if abs(m) < eps:
            raise ZeroDivisionError(f"TDMA: division by zero on step {i}")
        if i < n - 1:
            cp[i] = c[i] / m
        fp[i] = (f[i] - a[i] * fp[i - 1]) / m

    # Обратный ход: восстановление y_i
    y = [0.0] * (n + 2)   # y[0] и y[n+1] — границы, y[1..n] — внутренняя сетка

    y[n] = fp[n - 1]      # y_N
    for i in range(n - 2, -1, -1):
        # i идёт от N-2 до 0, а индекс для y сдвигаем на +1
        y[i + 1] = fp[i] - cp[i] * y[i + 2]

    return y
