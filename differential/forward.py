def forward_pass(a, b, c, f, eps=1e-15):
    """
    Прямой ход метода прогонки (TDMA).
    
    a, b, c — коэффициенты трёхдиагональной матрицы
    f — правая часть
    """

    n = len(f)

    # Массивы α_i (cp) и β_i (fp)
    cp = [0.0] * n
    fp = [0.0] * n

    # --- Шаг 1. Начальные коэффициенты ---
    if abs(b[0]) < eps:
        raise ZeroDivisionError("Прогонка: деление на ноль при i = 0")

    cp[0] = c[0] / b[0]
    fp[0] = f[0] / b[0]

    # --- Шаг 2. Рекуррентные формулы ---
    for i in range(1, n):
        m = b[i] - a[i] * cp[i - 1]
        if abs(m) < eps:
            raise ZeroDivisionError(f"Прогонка: деление на ноль при i = {i}")

        if i < n - 1:
            cp[i] = c[i] / m

        fp[i] = (f[i] - a[i] * fp[i - 1]) / m

    return cp, fp
