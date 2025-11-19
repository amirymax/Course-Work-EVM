'''
Метод Симпсона для вычисления интеграла
'''

def simpson(f, a, b, n):
    # n must be even
    if n % 2 != 0:
        raise ValueError("Для метода Симпсона число разбиений n должно быть чётным.")

    h = (b - a) / n
    s = f(a) + f(b)

    # Сумма нечётных узлов (коэффициент 4)
    for i in range(1, n, 2):
        x = a + i * h
        s += 4 * f(x)

    # Сумма чётных узлов (коэффициент 2)
    for i in range(2, n, 2):
        x = a + i * h
        s += 2 * f(x)

    return s * h / 3
