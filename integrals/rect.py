'''
Методы Прямоугольников для вычисления интегралов

'''


def left_rect(f, a, b, n):
    h = (b - a) / n
    s = 0
    for i in range(n):
        x = a + i * h
        s += f(x)
    return s * h

def right_rect(f, a, b, n):
    h = (b - a) / n
    s = 0
    x = a + h
    for i in range(n):
        s += f(x)
        x += h
    return s * h
