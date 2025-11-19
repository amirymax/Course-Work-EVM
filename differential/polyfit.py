import numpy as np


def canonical_poly_coeffs(xs, ys):
    """
    Находит коэффициенты канонического интерполяционного полинома
    по узлам xs и значениям ys.

    P(x) = a0 + a1*x + ... + a_{n-1}*x^{n-1}

    :param xs: последовательность x_i (list/tuple/np.array)
    :param ys: последовательность y_i (той же длины)
    :return: numpy-массив коэффициентов a (длина n)
    """
    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)

    if xs.shape != ys.shape:
        raise ValueError("xs и ys должны иметь одинаковую длину")

    n = len(xs)

    # Вандермондова матрица: столбцы [1, x, x^2, ..., x^{n-1}]
    # increasing=True -> степени растут слева направо
    X = np.vander(xs, N=n, increasing=True)

    # Решаем систему X * a = y
    coeffs = np.linalg.solve(X, ys)
    return coeffs


def canonical_poly_to_str(coeffs, eps=1e-8):
    """
    Строит человекочитаемую строку вида
    a0 + a1*x + a2*x^2 + ...

    :param coeffs: последовательность коэффициентов a_i
    :param eps: порог, ниже которого коэффициент считаем нулём
    :return: строка с формулой полинома
    """
    terms = []

    for power, a in enumerate(coeffs):
        if abs(a) < eps:
            continue  # мелкие коэффициенты игнорируем

        # модуль и степень
        abs_a = abs(a)

        # аккуратное форматирование числа
        coef_str = f"{abs_a:.6f}".rstrip("0").rstrip(".")
        if coef_str == "":
            coef_str = "0"

        if power == 0:
            term = coef_str
        elif power == 1:
            term = f"{coef_str} * x"
        else:
            term = f"{coef_str} * x^{power}"

        sign = "-" if a < 0 else "+"
        terms.append((sign, term))

    if not terms:
        return "0"

    # первый член: знак только если он минус
    first_sign, first_term = terms[0]
    formula = ("-" if first_sign == "-" else "") + first_term

    # остальные с явными знаками
    for sign, term in terms[1:]:
        formula += f" {sign} {term}"

    return formula


def polyfit_canonical(xs, ys):
    """
    Удобная обёртка:
    возвращает и коэффициенты, и текстовую формулу.

    :param xs: узлы x_i
    :param ys: значения y_i
    :return: (coeffs, formula_str)
    """
    coeffs = canonical_poly_coeffs(xs, ys)
    formula = canonical_poly_to_str(coeffs)
    return coeffs, formula


if __name__ == "__main__":
    # маленький пример теста:
    xs_example = [ -1.0, 0.0, 1.0 ]
    ys_example = [  2.0, 1.0, 2.0 ]

    coeffs, formula = polyfit_canonical(xs_example, ys_example)
    print("Коэффициенты:", coeffs)
    print("P(x) =", formula)
