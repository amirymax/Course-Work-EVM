"""
Этап отделения корней.
Ищет первый отрезок [a, b], на котором:
    1) f(a) * f(b) < 0  — функция меняет знак;
    2) fp(a) * fp(b) > 0 — первая производная сохраняет знак;
    3) fpp(a) * fpp(b) > 0 — вторая производная сохраняет знак.
Если подходящий отрезок не найден, выбрасывает исключение.

"""

from typing import Callable, Tuple


def separate_root(
    f: Callable[[float], float],
    fp: Callable[[float], float],
    fpp: Callable[[float], float],
    a_start: float = -10.0,
    step: float = 0.5,
    max_steps: int = 1000,
) -> Tuple[float, float]:
    
    a = a_start
    b = a + step

    for _ in range(max_steps):
        fa = f(a)
        fb = f(b)

        if fa * fb < 0:
            fpa = fp(a)
            fpb = fp(b)

            if fpa * fpb > 0:
                fppa = fpp(a)
                fppb = fpp(b)

                if fppa * fppb > 0:
                    # нашли подходящий интервал отделения корня
                    return a, b

        # двигаем окно на следующий отрезок
        a = b
        b = a + step

    raise ValueError("Не удалось найти отрезок, удовлетворяющий условиям отделения корня.")
