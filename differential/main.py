import sys
import math
import numpy as np

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QRadioButton,
    QButtonGroup, QLabel, QTableWidget,
    QTableWidgetItem, QGroupBox, QFrame
)
from PySide6.QtCore import Qt

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# ---------- математика МКР ----------

def make_func(expr: str):
    """Строка вида '-x', 'x**2', '2*x+1' -> функция f(x)."""
    expr = (expr or "").strip()
    if not expr:
        return lambda x: 0.0

    def f(x):
        return float(eval(expr, {"x": x, "np": np, "math": math}))
    return f


def build_grid(x0: float, xk: float, n: int):
    """Равномерная сетка: n отрезков -> n+1 узлов."""
    h = (xk - x0) / n
    xs = np.array([x0 + i * h for i in range(n + 1)], dtype=float)
    return xs, h


def assemble_tridiagonal(xs, h, p_expr, q_expr, f_expr):
    """
    Коэффициенты трёхдиагональной системы для
    y'' + p(x) y' + q(x) y = f(x) в узлах x1..x_{n-1}.
    """
    p = make_func(p_expr)
    q = make_func(q_expr)
    f = make_func(f_expr)

    n = len(xs) - 1     # число отрезков
    m = n - 1           # внутренних узлов

    a = np.zeros(m)     # поддиагональ
    b = np.zeros(m)     # диагональ
    c = np.zeros(m)     # наддиагональ
    rhs = np.zeros(m)   # правая часть

    for i in range(1, n):    # i = 1..n-1
        xi = xs[i]
        pi = p(xi)
        qi = q(xi)
        fi = f(xi)

        k = i - 1
        a[k] = 1.0 - pi * h / 2.0
        b[k] = -2.0 + (h ** 2) * qi
        c[k] = 1.0 + pi * h / 2.0
        rhs[k] = (h ** 2) * fi

    return a, b, c, rhs


def apply_boundary_conditions(a, c, rhs, y0, yk):
    """Учет граничных условий y(x0)=y0, y(xk)=yk в правой части."""
    rhs = rhs.copy()
    rhs[0] -= a[0] * y0
    rhs[-1] -= c[-1] * yk
    return rhs


def thomas_solve(a, b, c, rhs):
    """Метод прогонки (Thomas) для трёхдиагональной системы."""
    n = len(b)
    alpha = np.zeros(n)
    beta = np.zeros(n)

    eps = 1e-14

    denom = b[0]
    if abs(denom) < eps:
        raise ZeroDivisionError("Division by zero in Thomas algorithm")

    alpha[0] = c[0] / denom
    beta[0] = rhs[0] / denom

    for i in range(1, n):
        denom = b[i] - a[i] * alpha[i - 1]
        if abs(denom) < eps:
            raise ZeroDivisionError("Division by zero in Thomas algorithm")
        alpha[i] = c[i] / denom if i < n - 1 else 0.0
        beta[i] = (rhs[i] - a[i] * beta[i - 1]) / denom

    # обратный ход
    y = np.zeros(n)
    y[-1] = beta[-1]
    for i in range(n - 2, -1, -1):
        y[i] = beta[i] - alpha[i] * y[i + 1]

    return y


def matrix_solve(a, b, c, rhs):
    """Решение через полную матрицу (матричный способ)."""
    n = len(b)
    A = np.zeros((n, n))
    np.fill_diagonal(A, b)
    np.fill_diagonal(A[1:, :-1], a[1:])
    np.fill_diagonal(A[:-1, 1:], c[:-1])
    return np.linalg.solve(A, rhs)


def solve_fdm(p_expr, q_expr, f_expr, x0, xk, y0, yk, n, method="thomas"):
    """Полное решение задачи МКР."""
    xs, h = build_grid(x0, xk, n)
    a, b, c, rhs = assemble_tridiagonal(xs, h, p_expr, q_expr, f_expr)
    rhs_bc = apply_boundary_conditions(a, c, rhs, y0, yk)

    if method == "matrix":
        y_inner = matrix_solve(a, b, c, rhs_bc)
    else:
        y_inner = thomas_solve(a, b, c, rhs_bc)

    ys = np.zeros_like(xs)
    ys[0] = y0
    ys[-1] = yk
    ys[1:-1] = y_inner
    return xs, ys


def build_approx(xs, ys, degree=None):
    """
    Строит аппроксимационный полином МНК.
    Работает даже при одинаковых x (дубликаты удаляются).
    """
    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)

    # Убираем повторяющиеся x
    xs, unique_indices = np.unique(xs, return_index=True)
    ys = ys[unique_indices]

    if degree is None:
        degree = min(5, len(xs) - 1)

    X = np.vander(xs, degree + 1, increasing=True)
    XtX = X.T @ X
    XtY = X.T @ ys
    coeffs = np.linalg.solve(XtX, XtY)
    return coeffs


def poly_to_string(coeffs, precision=4):
    """Красивый текст P(x) = ..."""
    parts = []
    for power, a in enumerate(coeffs):
        if abs(a) < 10 ** (-precision - 1):
            continue

        if not parts:
            sign = ""      # первый член
            value = a
        else:
            sign = " + " if a >= 0 else " - "
            value = abs(a)

        value_str = f"{value:.{precision}f}"

        if power == 0:
            term = value_str
        elif power == 1:
            term = f"{value_str} * x"
        else:
            term = f"{value_str} * x^{power}"

        parts.append(sign + term)

    return "P(x) = " + ("".join(parts) if parts else "0")


# ---------- PySide6 GUI ----------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Метод конечных разностей (МКР)")
        self.resize(1180, 640)

        self._setup_styles()
        self._build_ui()

    def _setup_styles(self):
        # общий стиль: светлый фон, синий акцент
        self.setStyleSheet("""
            QMainWindow {
                background: #f4f6fb;
            }
            QWidget#Card {
                background: #ffffff;
                border: 1px solid #d0d7de;
                border-radius: 6px;
            }
            QLabel {
                font-family: "Segoe UI";
                font-size: 10pt;
            }
            QLabel.header {
                font-size: 12pt;
                font-weight: 600;
            }
            QLineEdit {
                padding: 4px 6px;
                border-radius: 4px;
                border: 1px solid #d0d7de;
                background: #ffffff;
                selection-background-color: #1f6feb;
            }
            QPushButton.accent {
                background: #1f6feb;
                color: white;
                border-radius: 6px;
                padding: 6px 10px;
                font-weight: 600;
            }
            QPushButton.accent:hover {
                background: #255fcc;
            }
            QGroupBox {
                border: 0px;
                margin-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 0 4px 0;
                font-weight: 600;
                color: #24292f;
            }
            QTableWidget {
                gridline-color: #d0d7de;
                font-size: 9pt;
            }
        """)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # левая панель
        left_card = QWidget(objectName="Card")
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(12, 10, 12, 10)
        left_layout.setSpacing(10)

        lbl_left = QLabel("Параметры задачи", objectName="header")
        lbl_left.setProperty("class", "header")
        lbl_left.setStyleSheet("QLabel { font-size: 12pt; font-weight: 600; }")
        left_layout.addWidget(lbl_left)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        self.p_edit = QLineEdit()
        self.q_edit = QLineEdit()
        self.f_edit = QLineEdit()
        form.addRow("p(x):", self.p_edit)
        form.addRow("q(x):", self.q_edit)
        form.addRow("f(x):", self.f_edit)

        self.x0_edit = QLineEdit()
        self.y0_edit = QLineEdit()
        self.xk_edit = QLineEdit()
        self.yk_edit = QLineEdit()
        self.n_edit = QLineEdit()

        form.addRow("x₀:", self.x0_edit)
        form.addRow("y(x₀):", self.y0_edit)
        form.addRow("xₖ:", self.xk_edit)
        form.addRow("y(xₖ):", self.yk_edit)
        form.addRow("n (отрезков):", self.n_edit)

        left_layout.addLayout(form)

        self.btn_auto = QPushButton("Заполнить по условию")
        self.btn_auto.setObjectName("accent")
        self.btn_auto.setProperty("class", "accent")
        self.btn_auto.setStyleSheet("QPushButton.accent{}")
        self.btn_auto.clicked.connect(self.fill_default)
        left_layout.addWidget(self.btn_auto)

        method_group_box = QGroupBox("Метод решения")
        method_layout = QVBoxLayout(method_group_box)

        self.rb_thomas = QRadioButton("Прогонка")
        self.rb_matrix = QRadioButton("Матричный способ")
        self.rb_thomas.setChecked(True)

        self.method_group = QButtonGroup(self)
        self.method_group.addButton(self.rb_thomas)
        self.method_group.addButton(self.rb_matrix)

        method_layout.addWidget(self.rb_thomas)
        method_layout.addWidget(self.rb_matrix)

        left_layout.addWidget(method_group_box)

        self.btn_calc = QPushButton("Рассчитать")
        self.btn_calc.setObjectName("accent")
        self.btn_calc.setProperty("class", "accent")
        self.btn_calc.setStyleSheet("QPushButton.accent{}")
        self.btn_calc.clicked.connect(self.calculate)
        left_layout.addWidget(self.btn_calc)

        left_layout.addStretch()

        # центральная панель
        center_card = QWidget(objectName="Card")
        center_layout = QVBoxLayout(center_card)
        center_layout.setContentsMargins(12, 10, 12, 10)
        center_layout.setSpacing(8)

        lbl_center = QLabel("Результаты", objectName="header")
        lbl_center.setStyleSheet("QLabel { font-size: 12pt; font-weight: 600; }")
        center_layout.addWidget(lbl_center)

        lbl_poly = QLabel("Интерполяционный полином:")
        center_layout.addWidget(lbl_poly)

        self.poly_edit = QLineEdit()
        self.poly_edit.setReadOnly(True)
        center_layout.addWidget(self.poly_edit)

        # таблица значений
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["x", "y(x)"])
        self.table.horizontalHeader().setStretchLastSection(True)
        center_layout.addWidget(self.table)

        # правая панель
        right_card = QWidget(objectName="Card")
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(12, 10, 12, 10)
        right_layout.setSpacing(8)

        lbl_right = QLabel("График решения", objectName="header")
        lbl_right.setStyleSheet("QLabel { font-size: 12pt; font-weight: 600; }")
        right_layout.addWidget(lbl_right)

        # matplotlib canvas
        self.figure = Figure(figsize=(4.5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("МКР")
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("y")
        self.ax.grid(True, alpha=0.3)

        self.canvas = FigureCanvas(self.figure)
        right_layout.addWidget(self.canvas, stretch=1)

        hint = QLabel(
            "Квадратные маркеры — значения в узлах сетки.\n"
            "Линия — канонический полином по решению."
        )
        hint.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(hint)

        # добавить карточки в основной layout
        main_layout.addWidget(left_card, stretch=0)
        main_layout.addWidget(center_card, stretch=1)
        main_layout.addWidget(right_card, stretch=1)

    # ---------- логика GUI ----------

    def fill_default(self):
        """Заполнение полей для варианта из задания."""
        # y'' - y' * x + x^2 y = 2x + 1; y(1) = 0; y(2) = 2; n = 8
        self.p_edit.setText("-x")
        self.q_edit.setText("x**2")
        self.f_edit.setText("2*x + 1")

        self.x0_edit.setText("1")
        self.y0_edit.setText("0")
        self.xk_edit.setText("2")
        self.yk_edit.setText("2")
        self.n_edit.setText("8")

    def calculate(self):
        try:
            p_expr = self.p_edit.text()
            q_expr = self.q_edit.text()
            f_expr = self.f_edit.text()

            x0 = float(self.x0_edit.text())
            xk = float(self.xk_edit.text())
            y0 = float(self.y0_edit.text())
            yk = float(self.yk_edit.text())
            n = int(self.n_edit.text())

            if n < 1:
                raise ValueError("n должно быть положительным")
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Ошибка ввода", f"Проверь значения: {e}")
            return

        method = "matrix" if self.rb_matrix.isChecked() else "thomas"

        try:
            xs, ys = solve_fdm(p_expr, q_expr, f_expr, x0, xk, y0, yk, n, method)
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Ошибка вычислений", str(e))
            return

        # полином
        try:
            coeffs = build_approx(xs, ys)
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Ошибка вычислений", str(e))
            return
        poly_str = poly_to_string(coeffs, precision=4)
        self.poly_edit.setText(poly_str)

        # таблица
        self.table.setRowCount(len(xs))
        for i, (x, y) in enumerate(zip(xs, ys)):
            self.table.setItem(i, 0, QTableWidgetItem(f"{x:.4f}"))
            self.table.setItem(i, 1, QTableWidgetItem(f"{y:.6f}"))

        # график
        self.ax.clear()
        self.ax.grid(True, alpha=0.3)
        self.ax.set_title("МКР")
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("y")

        # точки
        self.ax.plot(xs, ys, marker="s", linestyle="None", label="Узлы сетки")

        # линия полинома
        poly_desc = coeffs[::-1]          # poly1d ждёт от старшей степени
        poly = np.poly1d(poly_desc)
        x_dense = np.linspace(xs[0], xs[-1], 400)
        y_dense = poly(x_dense)
        self.ax.plot(x_dense, y_dense, linewidth=2, label="Полином")

        self.ax.legend(loc="best")
        self.canvas.draw_idle()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
