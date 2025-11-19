'''
Нахождение минимального n, при котором все методы совпадают
'''

from rect import left_rect, right_rect
from trapezoid import trapezoid
from simpson import simpson


def rounded3(x):
    """Округляет число до 3 знаков после запятой (как в VBA)."""
    return round(x, 3)


def find_min_n(f, a, b):
    """
    Находит минимальное чётное n, при котором результаты
    всех методов совпадают до 3 знаков.
    """

    n = 2  # симпсон требует n кратного 2

    while True:
        # вычисление значений всеми методами
        L = rounded3(left_rect(f, a, b, n))
        R = rounded3(right_rect(f, a, b, n))
        T = rounded3(trapezoid(f, a, b, n))
        S = rounded3(simpson(f, a, b, n))

        # проверка совпадения (как в VBA)
        if L == R == T == S:
            return n, L  # минимальное n и само значение

        n += 2
        if n > 100000:
            raise RuntimeError("Не удалось найти n — слишком большой перебор")