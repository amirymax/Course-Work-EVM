def evaluate_expression(expr: str, x_value: float) -> float:
    """
    Вычисляет выражение вида '2*x + 1' при заданном x_value.
    Разрешены только безопасные операции.
    """
    allowed = {"x": x_value}
    return eval(expr, {"__builtins__": {}}, allowed)


def approximate_p_q_f(expr_p: str, expr_q: str, expr_f: str, x_nodes: list):
    """
    Возвращает значения p(x), q(x), f(x) во всех узлах сетки.
    
    expr_p, expr_q, expr_f — строки с выражением (например: '2*x + 1')
    x_nodes — список узлов сетки
    """
    p_vals = []
    q_vals = []
    f_vals = []

    for x in x_nodes:
        p_vals.append(evaluate_expression(expr_p, x))
        q_vals.append(evaluate_expression(expr_q, x))
        f_vals.append(evaluate_expression(expr_f, x))

    return p_vals, q_vals, f_vals


expr_p = "2*x"       # p(x)
expr_q = "x**2"      # q(x)
expr_f = "2*x + 1"   # f(x)

x_nodes = [1.0, 1.25, 1.5, 1.75, 2.0]

p, q, f = approximate_p_q_f(expr_p, expr_q, expr_f, x_nodes)

print("p(x):", p)
print("q(x):", q)
print("f(x):", f)



