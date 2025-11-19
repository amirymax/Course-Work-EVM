from __future__ import annotations

from typing import List, Tuple

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QListWidget,
    QMessageBox,
    QSizePolicy,
    QFormLayout 
)
from PySide6.QtCore import Qt

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from linear import linear_least_squares
from quadratic import quadratic_least_squares
from reciprocal import reciprocal_least_squares


# --- данные варианта (можно подредактировать под свою таблицу) ---
DEFAULT_POINTS: List[Tuple[float, float]] = [
    (0.07, 0.00912),
    (0.09, 0.00127),
    (0.11, 0.0119),
    (0.22, 0.0130),
    (0.33, 0.0320),
    (0.44, 0.0330),
    (0.55, 0.0330),
    (0.66, 0.0320),
    (0.77, 0.0270),
    (0.88, 0.0180),
    (0.99, 0.0041),
    (1.00, 0.0020),
]


class LSMWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Метод наименьших квадратов")
        self.resize(1150, 600)

        self.x_vals: List[float] = []
        self.y_vals: List[float] = []

        self._build_ui()
        self._apply_styles()

    # ---------- UI ----------

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(10)

        # ЛЕВАЯ ПАНЕЛЬ — точки
        root_layout.addWidget(self._build_points_panel(), 0)

        # СРЕДНЯЯ ПАНЕЛЬ — коэффициенты
        root_layout.addWidget(self._build_coeffs_panel(), 0)

        # ПРАВАЯ ПАНЕЛЬ — график
        root_layout.addWidget(self._build_plot_panel(), 1)

    def _build_points_panel(self) -> QGroupBox:
        box = QGroupBox("Экспериментальные данные")
        layout = QVBoxLayout(box)
        layout.setSpacing(8)

        # точка для добавления
        add_row = QHBoxLayout()
        self.edit_x_new = QLineEdit()
        self.edit_y_new = QLineEdit()
        self.edit_x_new.setPlaceholderText("x")
        self.edit_y_new.setPlaceholderText("y")
        add_row.addWidget(self.edit_x_new)
        add_row.addWidget(self.edit_y_new)
        layout.addLayout(add_row)

        # кнопки управления
        btn_add = QPushButton("Добавить точку")
        btn_auto = QPushButton("Заполнить по условию")
        btn_delete = QPushButton("Удалить выделенную")
        btn_clear = QPushButton("Очистить все")

        btn_add.clicked.connect(self.on_add_point)
        btn_auto.clicked.connect(self.on_auto_fill)
        btn_delete.clicked.connect(self.on_delete_selected)
        btn_clear.clicked.connect(self.on_clear_all)

        layout.addWidget(btn_add)
        layout.addWidget(btn_auto)
        layout.addWidget(btn_delete)
        layout.addWidget(btn_clear)

        # списки X и Y
        lists_row = QHBoxLayout()
        self.list_x = QListWidget()
        self.list_y = QListWidget()
        self.list_x.setMinimumWidth(80)
        self.list_y.setMinimumWidth(80)
        lists_row.addWidget(self.list_x)
        lists_row.addWidget(self.list_y)
        layout.addLayout(lists_row)

        return box

    def _build_coeffs_panel(self) -> QGroupBox:
        box = QGroupBox("Аппроксимации МНК")
        layout = QVBoxLayout(box)
        layout.setSpacing(10)

        # --- Линейная модель ---
        gb_lin = QGroupBox("Линейная модель")
        lin_layout = QVBoxLayout(gb_lin)

        lin_layout.addWidget(QLabel("Модель:  y ≈ a·x + b"))

        form_lin = QFormLayout()
        form_lin.setLabelAlignment(Qt.AlignRight)

        self.lin_a = QLineEdit()
        self.lin_b = QLineEdit()
        self.lin_sumsq = QLineEdit()
        for e in (self.lin_a, self.lin_b, self.lin_sumsq):
            e.setReadOnly(True)

        form_lin.addRow("a =", self.lin_a)
        form_lin.addRow("b =", self.lin_b)
        form_lin.addRow("S = Σ (y - f(x))² =", self.lin_sumsq)

        lin_layout.addLayout(form_lin)
        layout.addWidget(gb_lin)

        # --- Квадратичная модель ---
        gb_quad = QGroupBox("Квадратичная модель")
        quad_layout = QVBoxLayout(gb_quad)

        quad_layout.addWidget(QLabel("Модель:  y ≈ a·x² + b·x + c"))

        form_quad = QFormLayout()
        form_quad.setLabelAlignment(Qt.AlignRight)

        self.quad_a = QLineEdit()
        self.quad_b = QLineEdit()
        self.quad_c = QLineEdit()
        self.quad_sumsq = QLineEdit()
        for e in (self.quad_a, self.quad_b, self.quad_c, self.quad_sumsq):
            e.setReadOnly(True)

        form_quad.addRow("a =", self.quad_a)
        form_quad.addRow("b =", self.quad_b)
        form_quad.addRow("c =", self.quad_c)
        form_quad.addRow("S = Σ (y - f(x))² =", self.quad_sumsq)

        quad_layout.addLayout(form_quad)
        layout.addWidget(gb_quad)

        # --- Обратная модель ---
        gb_rec = QGroupBox("Обратная модель")
        rec_layout = QVBoxLayout(gb_rec)

        rec_layout.addWidget(QLabel("Модель:  y ≈ a / x + b"))

        form_rec = QFormLayout()
        form_rec.setLabelAlignment(Qt.AlignRight)

        self.rec_a = QLineEdit()
        self.rec_b = QLineEdit()
        self.rec_sumsq = QLineEdit()
        for e in (self.rec_a, self.rec_b, self.rec_sumsq):
            e.setReadOnly(True)

        form_rec.addRow("a =", self.rec_a)
        form_rec.addRow("b =", self.rec_b)
        form_rec.addRow("S = Σ (y - f(x))² =", self.rec_sumsq)

        rec_layout.addLayout(form_rec)
        layout.addWidget(gb_rec)

        # --- кнопка расчёта ---
        self.btn_calculate = QPushButton("Рассчитать и построить график")
        self.btn_calculate.clicked.connect(self.on_calculate)
        layout.addWidget(self.btn_calculate)

        return box

    def _build_plot_panel(self) -> QGroupBox:
        box = QGroupBox("График аппроксимаций")
        v = QVBoxLayout(box)

        self.figure = Figure(figsize=(5, 4), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        v.addWidget(self.canvas)

        self.label_hint = QLabel(
            "Круглые маркеры — экспериментальные точки.\n"
            "Линии — линейная, квадратичная и обратная аппроксимации."
        )
        self.label_hint.setAlignment(Qt.AlignCenter)
        v.addWidget(self.label_hint)

        self._clear_plot()

        return box

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #e5edf7;
            }
            QGroupBox {
                border: 1px solid #cbd5e1;
                border-radius: 10px;
                margin-top: 10px;
                background-color: #f9fafb;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 4px;
                font-weight: 600;
                color: #1f2933;
            }
            QPushButton {
                background-color: #2563eb;
                color: white;
                border-radius: 6px;
                padding: 6px 10px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
            }
            QLineEdit, QListWidget {
                background-color: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 3px 4px;
            }
            QLabel {
                color: #111827;
            }
            """
        )

    # ---------- Работа с точками ----------

    def refresh_lists(self) -> None:
        self.list_x.clear()
        self.list_y.clear()

        for xv, yv in zip(self.x_vals, self.y_vals):
            self.list_x.addItem(f"{xv:g}")
            self.list_y.addItem(f"{yv:g}")

    def on_add_point(self) -> None:
        try:
            x = float(self.edit_x_new.text().replace(",", "."))
            y = float(self.edit_y_new.text().replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректные числовые значения x и y.")
            return

        self.x_vals.append(x)
        self.y_vals.append(y)
        self.edit_x_new.clear()
        self.edit_y_new.clear()
        self.refresh_lists()
        self._clear_results()
        self._clear_plot()

    def on_auto_fill(self) -> None:
        self.x_vals = [p[0] for p in DEFAULT_POINTS]
        self.y_vals = [p[1] for p in DEFAULT_POINTS]
        self.refresh_lists()
        self._clear_results()
        self._clear_plot()

    def on_delete_selected(self) -> None:
        row = self.list_x.currentRow()
        if row < 0 or row >= len(self.x_vals):
            QMessageBox.information(self, "Удаление", "Выберите строку в списке X.")
            return

        del self.x_vals[row]
        del self.y_vals[row]
        self.refresh_lists()
        self._clear_results()
        self._clear_plot()

    def on_clear_all(self) -> None:
        self.x_vals.clear()
        self.y_vals.clear()
        self.refresh_lists()
        self._clear_results()
        self._clear_plot()

    # ---------- Расчёты и график ----------

    def _clear_results(self) -> None:
        for e in (
            self.lin_a,
            self.lin_b,
            self.lin_sumsq,
            self.quad_a,
            self.quad_b,
            self.quad_c,
            self.quad_sumsq,
            self.rec_a,
            self.rec_b,
            self.rec_sumsq,
        ):
            e.clear()

    def _clear_plot(self) -> None:
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_title("График появится после расчёта")
        ax.grid(True, linestyle="--", alpha=0.3)
        self.canvas.draw_idle()

    def on_calculate(self) -> None:
        if len(self.x_vals) < 3:
            QMessageBox.warning(self, "Недостаточно данных", "Нужно минимум 3 точки.")
            return

        x = self.x_vals
        y = self.y_vals

        # линейная
        a_lin, b_lin, s_lin = linear_least_squares(x, y)
        self.lin_a.setText(f"{a_lin:.6g}")
        self.lin_b.setText(f"{b_lin:.6g}")
        self.lin_sumsq.setText(f"{s_lin:.6g}")

        # квадратичная
        a_q, b_q, c_q, s_q = quadratic_least_squares(x, y)
        self.quad_a.setText(f"{a_q:.6g}")
        self.quad_b.setText(f"{b_q:.6g}")
        self.quad_c.setText(f"{c_q:.6g}")
        self.quad_sumsq.setText(f"{s_q:.6g}")

        # обратная
        a_r, b_r, s_r = reciprocal_least_squares(x, y)
        self.rec_a.setText(f"{a_r:.6g}")
        self.rec_b.setText(f"{b_r:.6g}")
        self.rec_sumsq.setText(f"{s_r:.6g}")

        self._update_plot(
            x,
            y,
            (a_lin, b_lin),
            (a_q, b_q, c_q),
            (a_r, b_r),
        )

    def _update_plot(
        self,
        x_vals: List[float],
        y_vals: List[float],
        lin_params: Tuple[float, float],
        quad_params: Tuple[float, float, float],
        rec_params: Tuple[float, float],
    ) -> None:
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.grid(True, linestyle="--", alpha=0.3)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_title("Аппроксимация МНК")

        # исходные точки
        ax.scatter(x_vals, y_vals, label="Экспериментальные точки")

        if not x_vals:
            self.canvas.draw_idle()
            return

        x_min, x_max = min(x_vals), max(x_vals)
        if x_min == x_max:
            x_min -= 1.0
            x_max += 1.0

        xs_dense = [
            x_min + i * (x_max - x_min) / 200.0 for i in range(201)
        ]

        a_lin, b_lin = lin_params
        a_q, b_q, c_q = quad_params
        a_r, b_r = rec_params

        # кривые
        ys_lin = [a_lin * x + b_lin for x in xs_dense]
        ys_quad = [a_q * x * x + b_q * x + c_q for x in xs_dense]
        ys_rec = [a_r / x + b_r for x in xs_dense if x != 0]

        # для обратной модели xs_dense и ys_rec должны совпасть по длине
        xs_rec = [x for x in xs_dense if x != 0]

        ax.plot(xs_dense, ys_lin, label="Линейная")
        ax.plot(xs_dense, ys_quad, label="Квадратичная")
        ax.plot(xs_rec, ys_rec, label="Обратная")

        ax.legend()
        self.canvas.draw_idle()


def main() -> None:
    app = QApplication([])
    win = LSMWindow()
    win.show()
    app.exec()


if __name__ == "__main__":
    main()
