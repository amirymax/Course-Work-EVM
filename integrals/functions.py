import math


def f1(x: float) -> float:
    """
    Интеграл 1 варианта №1:
    ∫ (sqrt(x^2 + 5)) / (2x + sqrt(x^2 - 0.5)) dx, [1.6; 2.4]
    """
    return math.sqrt(x**2 + 5) / (2 * x + math.sqrt(x**2 - 0.5))


def f2(x: float) -> float:
    """
    Интеграл 2 варианта №1:
    ∫ dx / sqrt(2x^2 - 1), [1.8; 2.6]
    """
    return 1.0 / math.sqrt(2 * x**2 - 1)
