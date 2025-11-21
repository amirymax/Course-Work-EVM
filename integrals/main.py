import sys
import os

from PySide6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QRadioButton, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from rect import left_rect, right_rect
from trapezoid import trapezoid
from simpson import simpson
from runge import runge_refine
from find_n import find_min_n
from functions import f1, f2


BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


class IntegralsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Численное интегрирование (Интегралы)")
        self.init_ui()
        self.setup_style()

    # ---------- UI ----------
    def init_ui(self):
        layout = QGridLayout(self)

        # === Блок значений a, b, n ===
        values_group = QGroupBox("Значения")
        v_layout = QGridLayout()

        self.a_edit = QLineEdit()
        self.b_edit = QLineEdit()
        self.n_edit = QLineEdit()

        v_layout.addWidget(QLabel("a:"), 0, 0)
        v_layout.addWidget(self.a_edit, 0, 1)
        v_layout.addWidget(QLabel("b:"), 1, 0)
        v_layout.addWidget(self.b_edit, 1, 1)
        v_layout.addWidget(QLabel("n:"), 2, 0)
        v_layout.addWidget(self.n_edit, 2, 1)

        values_group.setLayout(v_layout)

        # === Выбор интеграла (с картинками) ===
        integrals_group = QGroupBox("Интеграл")
        i_layout = QVBoxLayout()

        # первый интеграл
        row1 = QHBoxLayout()
        self.integral1_radio = QRadioButton()
        img1_label = QLabel()
        pix1 = QPixmap(os.path.join(ASSETS_DIR, "int1.png"))
        img1_label.setPixmap(pix1)
        img1_label.setAlignment(Qt.AlignCenter)
        row1.addWidget(self.integral1_radio)
        row1.addWidget(img1_label)
        i_layout.addLayout(row1)

        # второй интеграл
        row2 = QHBoxLayout()
        self.integral2_radio = QRadioButton()
        img2_label = QLabel()
        pix2 = QPixmap(os.path.join(ASSETS_DIR, "int2.png"))
        img2_label.setPixmap(pix2)
        img2_label.setAlignment(Qt.AlignCenter)
        row2.addWidget(self.integral2_radio)
        row2.addWidget(img2_label)
        i_layout.addLayout(row2)

        self.integral1_radio.setChecked(True)
        integrals_group.setLayout(i_layout)

        # === Результаты методов ===
        methods_group = QGroupBox("Методы")
        m_layout = QGridLayout()

        self.left_edit = QLineEdit()
        self.right_edit = QLineEdit()
        self.trap_edit = QLineEdit()
        self.simp_edit = QLineEdit()
        self.nmin_edit = QLineEdit()
        self.nmin_edit.setReadOnly(True)

        for w in (self.left_edit, self.right_edit, self.trap_edit, self.simp_edit):
            w.setReadOnly(True)

        m_layout.addWidget(QLabel("Левые прямоуг.:"), 0, 0)
        m_layout.addWidget(self.left_edit,          0, 1)
        m_layout.addWidget(QLabel("Правые прямоуг.:"), 1, 0)
        m_layout.addWidget(self.right_edit,         1, 1)
        m_layout.addWidget(QLabel("Трапеция:"),     2, 0)
        m_layout.addWidget(self.trap_edit,          2, 1)
        m_layout.addWidget(QLabel("Симпсон:"),      3, 0)
        m_layout.addWidget(self.simp_edit,          3, 1)
        m_layout.addWidget(QLabel("n_min:"),        4, 0)
        m_layout.addWidget(self.nmin_edit,          4, 1)

        methods_group.setLayout(m_layout)

        # === Кнопки действий ===
        calc_btn = QPushButton("Считать")
        calc_btn.clicked.connect(self.on_calculate)

        runge_btn = QPushButton("Рунге")
        runge_btn.clicked.connect(self.on_runge)

        nmin_btn = QPushButton("Найти n_min")
        nmin_btn.clicked.connect(self.on_find_nmin)

        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(calc_btn)
        buttons_layout.addWidget(runge_btn)
        buttons_layout.addWidget(nmin_btn)
        buttons_layout.addStretch()

        # --- Раскладка по сетке ---
        # 0-я строка: слева значения, справа интегралы
        layout.addWidget(values_group,    0, 0)
        layout.addWidget(integrals_group, 0, 1)

        # 1-я строка: слева методы, справа кнопки
        layout.addWidget(methods_group,   1, 0)
        layout.addLayout(buttons_layout,  1, 1)

        # чуть компактнее окно
        self.resize(750, 380)

    # ---------- Стиль ----------
    def setup_style(self):
        layout: QGridLayout = self.layout()
        layout.setColumnStretch(0, 4)   # широкая левая колонка (поля)
        layout.setColumnStretch(1, 3)   # правая колонка (интегралы + кнопки)

        # один размер для всех полей ввода/вывода
        for w in (
            self.a_edit, self.b_edit, self.n_edit,
            self.left_edit, self.right_edit, self.trap_edit,
            self.simp_edit, self.nmin_edit
        ):
            w.setFixedWidth(260)

        self.setStyleSheet("""
        QWidget {
            background-color: #f4f6fb;
            font-family: Segoe UI, Roboto, "Open Sans";
            font-size: 10pt;
        }

        QGroupBox {
            border: 1px solid #cfd4e6;
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 10px;
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
            border: 1px solid #c3c8da;
            border-radius: 4px;
            padding: 4px 6px;
            selection-background-color: #2f80ed;
        }

        QLineEdit[readOnly="true"] {
            background-color: #f0f2f8;
            color: #555;
        }

        QPushButton {
            background-color: #2f80ed;
            color: white;
            border-radius: 6px;
            padding: 6px 14px;
            font-weight: 600;
            border: none;
            min-width: 130px;
        }

        QPushButton:hover {
            background-color: #2567c4;
        }

        QPushButton:pressed {
            background-color: #1c4d91;
        }

        QRadioButton {
            spacing: 6px;
        }
        """)

        # пометить readOnly-поля явным свойством для стиля
        for w in (self.left_edit, self.right_edit,
                  self.trap_edit, self.simp_edit, self.nmin_edit):
            w.setProperty("readOnly", True)
            w.style().unpolish(w)
            w.style().polish(w)

    # ---------- Вспомогательное ----------
    def get_current_function(self):
        return f1 if self.integral1_radio.isChecked() else f2

    def read_abn(self, require_n=True):
        try:
            a = float(self.a_edit.text().replace(",", "."))
            b = float(self.b_edit.text().replace(",", "."))
        except ValueError:
            raise ValueError("Некорректное значение a или b")

        if require_n:
            try:
                n = int(self.n_edit.text())
            except ValueError:
                raise ValueError("Некорректное значение n")
            if n <= 0:
                raise ValueError("n должно быть положительным")
            return a, b, n
        else:
            return a, b, None

    # ---------- Обработчики ----------
    def on_calculate(self):
        try:
            a, b, n = self.read_abn(require_n=True)
            f = self.get_current_function()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", str(e))
            return

        if n % 2 != 0:
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Для метода Симпсона n должно быть чётным."
            )
            return

        try:
            left_val = left_rect(f, a, b, n)
            right_val = right_rect(f, a, b, n)
            trap_val = trapezoid(f, a, b, n)
            simp_val = simpson(f, a, b, n)
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", f"ОДЗ {e}")
            return
        self.left_edit.setText(f"{left_val:.6f}")
        self.right_edit.setText(f"{right_val:.6f}")
        self.trap_edit.setText(f"{trap_val:.6f}")
        self.simp_edit.setText(f"{simp_val:.6f}")

    def on_find_nmin(self):
        try:
            a, b, _ = self.read_abn(require_n=False)
            f = self.get_current_function()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", str(e))
            return

        try:
            n_min, value = find_min_n(f, a, b)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка при поиске n_min", str(e))
            return

        self.nmin_edit.setText(str(n_min))
        self.left_edit.setText(f"{value[0]}")
        self.right_edit.setText(f"{value[1]}")
        self.trap_edit.setText(f"{value[2]}")
        self.simp_edit.setText(f"{value[3]}")

    def on_runge(self):
        try:
            a, b, _ = self.read_abn(require_n=False)
            f = self.get_current_function()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", str(e))
            return

        eps = 1e-4
        try:
            I_left,  n_left  = runge_refine(left_rect,  f, a, b, n_start=4, eps=eps, p=1)
            I_right, n_right = runge_refine(right_rect, f, a, b, n_start=4, eps=eps, p=1)
            I_trap,  n_trap  = runge_refine(trapezoid,  f, a, b, n_start=4, eps=eps, p=2)
            I_simp,  n_simp  = runge_refine(simpson,    f, a, b, n_start=4, eps=eps, p=4)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка правила Рунге", str(e))
            return

        msg = (
            f"Результаты по правилу Рунге (eps={eps}):\n\n"
            f"Левые прямоугольники:  I = {I_left:.6f},  n = {n_left}\n"
            f"Правые прямоугольники: I = {I_right:.6f}, n = {n_right}\n"
            f"Трапеция:              I = {I_trap:.6f},  n = {n_trap}\n"
            f"Симпсон:               I = {I_simp:.6f},  n = {n_simp}"
        )
        QMessageBox.information(self, "Правило Рунге", msg)


def main():
    app = QApplication(sys.argv)
    window = IntegralsWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
