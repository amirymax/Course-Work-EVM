'''
Нахождение минимального n, при котором все методы совпадают
'''

from rect import left_rect, right_rect
from trapezoid import trapezoid
from simpson import simpson


def floor3(x):
    return int(x * 1000) / 1000



def find_min_n(f, a, b):
    n = 2
    while True:

        # НЕ ОКРУГЛЁННЫЕ значения
        L = left_rect(f, a, b, n)
        R = right_rect(f, a, b, n)
        T = trapezoid(f, a, b, n)
        S = simpson(f, a, b, n)

        # ОКРУГЛЁННЫЕ для проверки
        L3 = floor3(L)
        R3 = floor3(R)
        T3 = floor3(T)
        S3 = floor3(S)

        # Проверка совпадения до 3 знаков
        if L3 == R3 == T3 == S3:
            return n, (L, R, T, S)

        n += 2
        if n > 100000:
            raise RuntimeError("Слишком большой n, методы не сходятся")
