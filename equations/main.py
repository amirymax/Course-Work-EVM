import sys
import math
from io import BytesIO

import numpy as np
import matplotlib
matplotlib.use("Agg")  # рисуем в памяти, без отдельных окон
import matplotlib.pyplot as plt

from PySide6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QRadioButton, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


# ==========================
#   ФУНКЦИИ И ПРОИЗВОДНЫЕ
# ==========================

def f1(x: float) -> float:
    # x^3 + 1.3x^2 − 4.7 = 0
    return x**3 + 1.3 * x**2 - 4.7


def f1p(x: float) -> float:
    return 3 * x**2 + 2.6 * x


def f1pp(x: float) -> float:
    return 6 * x + 2.6


def phi1(x: float) -> float:
    # простая φ(x) для итерационного метода
    m = 10.0
    return x - f1(x) / m


def f2(x: float) -> float:
    # (x − 1)^2 = 0.5 e^x  →  (x − 1)^2 − 0.5 e^x = 0
    return (x - 1) ** 2 - 0.5 * math.exp(x)


def f2p(x: float) -> float:
    return 2 * (x - 1) - 0.5 * math.exp(x)


def f2pp(x: float) -> float:
    return 2 - 0.5 * math.exp(x)


def phi2(x: float) -> float:
    m = 5.0
    return x - f2(x) / m


# ==========================
#     ЧИСЛЕННЫЕ МЕТОДЫ
# ==========================

def dichotomy(f, a, b, eps, max_iter=100):
    n = 0
    while True:
        c = (a + b) / 2
        fc = f(c)

        if abs(fc) < eps:
            return c, n + 1

        if f(a) * fc < 0:
            b = c
        else:
            a = c

        n += 1
        if n > max_iter:
            raise RuntimeError("Метод дихотомии: превышено число итераций")


def chord(f, a, b, eps, max_iter=50):
    if f(a) * f(b) >= 0:
        raise ValueError("Метод хорд: на интервале нет смены знака функции")

    n = 0
    prev = b

    while True:
        bn = b - f(b) * (a - b) / (f(a) - f(b))
        n += 1

        if abs(bn - prev) <= eps:
            return bn, n

        if n > max_iter:
            raise RuntimeError("Метод хорд: превышено число итераций")

        prev = bn
        b = bn


def newton(f, fp, x0, eps, max_iter=50):
    x = x0
    n = 0

    while True:
        if fp(x) == 0:
            raise ZeroDivisionError("Метод Ньютона: производная равна 0")

        x_new = x - f(x) / fp(x)
        n += 1

        if abs(x_new - x) <= eps:
            return x_new, n

        if n > max_iter:
            raise RuntimeError("Метод Ньютона: превышено число итераций")

        x = x_new


def combined_method(f, fp, a, b, eps, max_iter=50):
    if f(a) * f(b) >= 0:
        raise ValueError("Комбинированный метод: неверный интервал [a, b]")

    n = 0
    while True:
        if fp(a) == 0 or fp(b) == 0:
            raise ZeroDivisionError("Комбинированный метод: производная = 0")

        an = a - f(a) / fp(a)                         # касательные слева
        bn = b - f(b) * (a - b) / (f(a) - f(b))       # хорды справа

        d = abs(bn - an)
        n += 1

        if d <= eps:
            return (an + bn) / 2.0, n

        if n > max_iter:
            raise RuntimeError("Комбинированный метод: превышено число итераций")

        a, b = an, bn


def iteration_method(phi, x0, eps, max_iter=50):
    x = x0
    n = 0
    while True:
        xn = phi(x)
        dx = abs(xn - x)
        n += 1

        if dx <= eps:
            return xn, n

        if n > max_iter:
            raise RuntimeError("Итерационный метод: итераций > 50")

        x = xn


def separate_root(f, fp, fpp, a_start=-10.0, step=0.5, max_steps=1000):
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
                    return a, b

        a = b
        b = a + step

    raise RuntimeError("Не удалось автоматически отделить корень")


def make_pixmap_for_function(f, a, b, root=None):
    x = np.linspace(a, b, 200)
    y = np.array([f(xi) for xi in x])

    fig, ax = plt.subplots(figsize=(4, 3), dpi=110)

    # линия функции
    ax.plot(x, y, label="f(x) — график функции")

    # ось X
    ax.axhline(0, color="black", linewidth=0.8)

    ax.set_xlabel("X")
    ax.set_ylabel("F(X)")
    ax.set_title("Equation graph")
    ax.grid(True)

    # точка корня
    if root is not None:
        ax.scatter(
            [root],
            [f(root)],
            s=40,
            color="red",
            label="x* — найденный корень",
        )

    # показываем легенду
    ax.legend(loc="best")

    buf = BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)

    pm = QPixmap()
    pm.loadFromData(buf.read())
    return pm


# ==========================
#         GUI КЛАСС
# ==========================

class EquationsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Нелинейные уравнения")
        self.init_ui()
        self.setup_style()

    def init_ui(self):
        layout = QGridLayout(self)

        # --- Уравнения ---
        eq_group = QGroupBox("Уравнения")
        eq_layout = QVBoxLayout()

        self.eq1_radio = QRadioButton("x³ + 1,3x² − 4,7 = 0")
        self.eq2_radio = QRadioButton("(x − 1)² = 0,5 eˣ")

        self.eq1_radio.setChecked(True)
        eq_layout.addWidget(self.eq1_radio)
        eq_layout.addWidget(self.eq2_radio)
        eq_group.setLayout(eq_layout)

        # --- Значения (a, b, e) ---
        vals_group = QGroupBox("Значения")
        vals_layout = QGridLayout()

        self.a_edit = QLineEdit("-2.5")
        self.b_edit = QLineEdit("-2.0")
        self.eps_edit = QLineEdit("0.0001")

        vals_layout.addWidget(QLabel("a"), 0, 0)
        vals_layout.addWidget(self.a_edit, 0, 1)
        vals_layout.addWidget(QLabel("b"), 1, 0)
        vals_layout.addWidget(self.b_edit, 1, 1)
        vals_layout.addWidget(QLabel("ε"), 2, 0)
        vals_layout.addWidget(self.eps_edit, 2, 1)

        vals_group.setLayout(vals_layout)

        # --- Методы ---
        methods_group = QGroupBox("Методы")
        m_layout = QGridLayout()

        self.dich_root = QLineEdit()
        self.chord_root = QLineEdit()
        self.newton_root = QLineEdit()
        self.comb_root = QLineEdit()
        self.iter_root = QLineEdit()

        self.dich_steps = QLineEdit()
        self.chord_steps = QLineEdit()
        self.newton_steps = QLineEdit()
        self.comb_steps = QLineEdit()
        self.iter_steps = QLineEdit()

        for w in (
            self.dich_root, self.chord_root, self.newton_root,
            self.comb_root, self.iter_root,
            self.dich_steps, self.chord_steps, self.newton_steps,
            self.comb_steps, self.iter_steps
        ):
            w.setReadOnly(True)

        m_layout.addWidget(QLabel(""), 0, 1)
        m_layout.addWidget(QLabel("x*"), 0, 1)
        m_layout.addWidget(QLabel("шаги"), 0, 2)

        m_layout.addWidget(QLabel("Дихотомии"), 1, 0)
        m_layout.addWidget(self.dich_root, 1, 1)
        m_layout.addWidget(self.dich_steps, 1, 2)

        m_layout.addWidget(QLabel("Хорды"), 2, 0)
        m_layout.addWidget(self.chord_root, 2, 1)
        m_layout.addWidget(self.chord_steps, 2, 2)

        m_layout.addWidget(QLabel("Касательные"), 3, 0)
        m_layout.addWidget(self.newton_root, 3, 1)
        m_layout.addWidget(self.newton_steps, 3, 2)

        m_layout.addWidget(QLabel("Комбинированный"), 4, 0)
        m_layout.addWidget(self.comb_root, 4, 1)
        m_layout.addWidget(self.comb_steps, 4, 2)

        m_layout.addWidget(QLabel("Итерационный"), 5, 0)
        m_layout.addWidget(self.iter_root, 5, 1)
        m_layout.addWidget(self.iter_steps, 5, 2)

        methods_group.setLayout(m_layout)

        # --- Кнопки ---
        self.auto_btn = QPushButton("Автоподбор")
        self.calc_btn = QPushButton("Считать")

        self.auto_btn.clicked.connect(self.on_auto)
        self.calc_btn.clicked.connect(self.on_calc)

        btn_layout = QVBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.auto_btn)
        btn_layout.addWidget(self.calc_btn)
        btn_layout.addStretch()

        # --- Область под график ---
        self.graph_label = QLabel()
        self.graph_label.setAlignment(Qt.AlignCenter)
        self.graph_label.setMinimumSize(320, 260)
        self.graph_label.setFrameShape(QLabel.Panel)
        self.graph_label.setFrameShadow(QLabel.Sunken)
        self.graph_label.setText("График функции")

        # --- Раскладка по сетке ---
        # верхний ряд
        layout.addWidget(eq_group,     0, 0)
        layout.addWidget(vals_group,   0, 1)
        layout.addWidget(self.graph_label, 0, 2, 2, 1)

        # нижний ряд
        layout.addWidget(methods_group, 1, 0)
        layout.addLayout(btn_layout,    1, 1)

        self.resize(1050, 480)

    def setup_style(self):
        for w in (
            self.a_edit, self.b_edit, self.eps_edit,
            self.dich_root, self.chord_root, self.newton_root,
            self.comb_root, self.iter_root,
            self.dich_steps, self.chord_steps, self.newton_steps,
            self.comb_steps, self.iter_steps
        ):
            w.setFixedWidth(130)

        self.setStyleSheet("""
        QWidget {
            background-color: #e8edf4;
            font-family: Segoe UI, Roboto, "Open Sans";
            font-size: 10pt;
        }
        QGroupBox {
            border: 1px solid #c0c8da;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 8px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 4px;
            color: #2c3e50;
            font-weight: 600;
        }
        QLabel {
            color: #34495e;
        }
        QLineEdit {
            background-color: #ffffff;
            border: 1px solid #c3c9dd;
            border-radius: 4px;
            padding: 3px 5px;
        }
        QLineEdit[readOnly="true"] {
            background-color: #f5f6fb;
            color: #555;
        }
        QPushButton {
            background-color: #2f80ed;
            color: white;
            border-radius: 6px;
            padding: 6px 14px;
            font-weight: 600;
            min-width: 130px;
        }
        QPushButton:hover {
            background-color: #2567c4;
        }
        QPushButton:pressed {
            background-color: #1b4d89;
        }
        """)

        # пометить readOnly для стиля
        for w in (
            self.dich_root, self.chord_root, self.newton_root,
            self.comb_root, self.iter_root,
            self.dich_steps, self.chord_steps, self.newton_steps,
            self.comb_steps, self.iter_steps
        ):
            w.setProperty("readOnly", True)
            w.style().unpolish(w)
            w.style().polish(w)

    # --------- Вспомогательное ---------

    def current_functions(self):
        if self.eq1_radio.isChecked():
            return f1, f1p, f1pp, phi1
        else:
            return f2, f2p, f2pp, phi2

    def read_params(self):
        try:
            a = float(self.a_edit.text().replace(",", "."))
            b = float(self.b_edit.text().replace(",", "."))
            eps = float(self.eps_edit.text().replace(",", "."))
        except ValueError:
            raise ValueError("Некорректные значения a, b или ε")
        if eps <= 0:
            raise ValueError("ε должно быть положительным")
        return a, b, eps

    # --------- СЛОТЫ ---------

    def on_auto(self):
        f, fp, fpp, _ = self.current_functions()
        try:
            a, b = separate_root(f, fp, fpp)
        except Exception as e:
            QMessageBox.warning(self, "Автоподбор", str(e))
            return

        self.a_edit.setText(f"{a:.4f}")
        self.b_edit.setText(f"{b:.4f}")

    def on_calc(self):
        f, fp, fpp, phi = self.current_functions()

        try:
            a, b, eps = self.read_params()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", str(e))
            return

        # очищаем
        for w in (
            self.dich_root, self.chord_root, self.newton_root,
            self.comb_root, self.iter_root,
            self.dich_steps, self.chord_steps, self.newton_steps,
            self.comb_steps, self.iter_steps
        ):
            w.clear()

        root_for_plot = None

        try:
            x_d, n_d = dichotomy(f, a, b, eps)
            self.dich_root.setText(f"{x_d:.6f}")
            self.dich_steps.setText(str(n_d))
            root_for_plot = x_d
        except Exception as e:
            self.dich_root.setText("-")
            self.dich_steps.setText("—")

        try:
            x_c, n_c = chord(f, a, b, eps)
            self.chord_root.setText(f"{x_c:.6f}")
            self.chord_steps.setText(str(n_c))
            root_for_plot = root_for_plot or x_c
        except Exception:
            self.chord_root.setText("-")
            self.chord_steps.setText("—")

        try:
            x_n, n_n = newton(f, fp, (a + b) / 2, eps)
            self.newton_root.setText(f"{x_n:.6f}")
            self.newton_steps.setText(str(n_n))
            root_for_plot = root_for_plot or x_n
        except Exception:
            self.newton_root.setText("-")
            self.newton_steps.setText("—")

        try:
            x_cb, n_cb = combined_method(f, fp, a, b, eps)
            self.comb_root.setText(f"{x_cb:.6f}")
            self.comb_steps.setText(str(n_cb))
            root_for_plot = root_for_plot or x_cb
        except Exception:
            self.comb_root.setText("-")
            self.comb_steps.setText("—")

        try:
            x_it, n_it = iteration_method(phi, (a + b) / 2, eps)
            self.iter_root.setText(f"{x_it:.6f}")
            self.iter_steps.setText(str(n_it))
            root_for_plot = root_for_plot or x_it
        except Exception:
            self.iter_root.setText("-")
            self.iter_steps.setText("—")

        # график
        try:
            pm = make_pixmap_for_function(f, a, b, root=root_for_plot)
            self.graph_label.setPixmap(pm)
        except Exception as e:
            QMessageBox.warning(self, "График", f"Не удалось построить график:\n{e}")


def main():
    app = QApplication(sys.argv)
    w = EquationsWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
