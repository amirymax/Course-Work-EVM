'''
Универсальная функция для использования правила Рунге
с всеми методами
'''

def runge_refine(method, f, a, b, n_start, eps, p):
    n = n_start
    while True:
        In  = method(f, a, b, n)
        I2n = method(f, a, b, 2 * n)
        delta = abs(I2n - In) / (2**p - 1)

        if delta < eps:
            return I2n, n      # найдено значение и количество разбиений

        n *= 2
        if n > 100000:
            raise RuntimeError("Не удалось добиться заданной точности")


