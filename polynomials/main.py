# polynomials/main.py

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont
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
    QListWidgetItem,
    QMessageBox,
)

# === импорт твоих методов интерполяции ===
from lagrange import lagrange                     # def lagrange(x_eval, xs, ys) -> float
from newton import newton_interpolation           # def newton_interpolation(x, xs, ys) -> float
from canon import canonical_polynomial            # def canonical_polynomial(x_eval, xs, ys) -> float
from graph import plot_graph                      # def plot_graph(xs, ys, title="Graph") -> str


APP_STYLES = """
QMainWindow {
    background-color: #edf1f7;
}

QGroupBox {
    background-color: #ffffff;
    border: 1px solid #d1d8e5;
    border-radius: 8px;
    margin-top: 14px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #34495e;
    font-weight: 600;
}

QLabel {
    color: #34495e;
}

QLineEdit, QListWidget {
    background-color: #fdfefe;
    border: 1px solid #c4ccdd;
    border-radius: 4px;
    padding: 4px 6px;
}

QListWidget {
    selection-background-color: #3498db;
    selection-color: #ffffff;
}

QPushButton {
    background-color: #3498db;
    color: #ffffff;
    border-radius: 6px;
    padding: 6px 10px;
    border: none;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #2d86c2;
}

QPushButton:pressed {
    background-color: #256999;
}

QPushButton[secondary="true"] {
    background-color: #ffffff;
    color: #3498db;
    border: 1px solid #3498db;
}

QPushButton[secondary="true"]:hover {
    background-color: #eaf4ff;
}

QPushButton[secondary="true"]:pressed {
    background-color: #d4e8ff;
}

#graphLabel {
    background-color: #ffffff;
    border: 1px dashed #c4ccdd;
    border-radius: 6px;
}

#legendLabel {
    color: #7f8c8d;
    font-style: italic;
}
"""


class PolyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Интерполяция таблично заданных функций")
        self.resize(1100, 600)

        # Чуть более приятный базовый шрифт
        font = QFont(self.font())
        font.setPointSize(9)
        self.setFont(font)

        # Центральный виджет
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # ===== ЛЕВАЯ КОЛОНКА: ввод точки и управление узлами =====
        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout, stretch=2)

        # --- Точка X* ---
        point_group = QGroupBox("Точка для интерполяции")
        pg_layout = QHBoxLayout(point_group)
        pg_layout.addWidget(QLabel("x*:"))
        self.le_x_eval = QLineEdit()
        self.le_x_eval.setPlaceholderText("например, 0.1")
        pg_layout.addWidget(self.le_x_eval)
        left_layout.addWidget(point_group)

        # --- Ввод одной пары (x, y) + кнопки управления ---
        pair_group = QGroupBox("Добавление узлов")
        pair_layout = QGridLayout(pair_group)
        pair_layout.setVerticalSpacing(6)

        pair_layout.addWidget(QLabel("x:"), 0, 0)
        self.le_x = QLineEdit()
        pair_layout.addWidget(self.le_x, 0, 1)

        pair_layout.addWidget(QLabel("y:"), 1, 0)
        self.le_y = QLineEdit()
        pair_layout.addWidget(self.le_y, 1, 1)

        self.btn_add = QPushButton("Добавить точку")
        self.btn_add.setProperty("secondary", True)

        self.btn_auto = QPushButton("Заполнить по условию")
        self.btn_auto.setProperty("secondary", True)

        self.btn_delete = QPushButton("Удалить выбранную")
        self.btn_delete.setProperty("secondary", True)

        self.btn_clear = QPushButton("Очистить все")
        self.btn_clear.setProperty("secondary", True)

        self.btn_add.setMinimumHeight(28)
        self.btn_auto.setMinimumHeight(28)
        self.btn_delete.setMinimumHeight(28)
        self.btn_clear.setMinimumHeight(28)

        pair_layout.addWidget(self.btn_add, 2, 0, 1, 2)
        pair_layout.addWidget(self.btn_auto, 3, 0, 1, 2)
        pair_layout.addWidget(self.btn_delete, 4, 0, 1, 2)
        pair_layout.addWidget(self.btn_clear, 5, 0, 1, 2)

        left_layout.addWidget(pair_group)

        # Кнопка "Рассчитать" внизу слева — основная
        self.btn_calc = QPushButton("Рассчитать полиномы")
        self.btn_calc.setMinimumHeight(40)
        left_layout.addWidget(self.btn_calc)

        left_layout.addStretch()

        # ===== ЦЕНТР: списки X и Y =====
        center_layout = QVBoxLayout()
        main_layout.addLayout(center_layout, stretch=3)

        lists_group = QGroupBox("Табличные данные")
        lg_layout = QHBoxLayout(lists_group)
        lg_layout.setContentsMargins(10, 10, 10, 10)

        self.list_x = QListWidget()
        self.list_y = QListWidget()
        self.list_x.setMinimumWidth(130)
        self.list_y.setMinimumWidth(130)

        lg_layout.addWidget(self._make_labeled_list("X", self.list_x))
        lg_layout.addWidget(self._make_labeled_list("Y", self.list_y))

        center_layout.addWidget(lists_group)

        # ===== ПРАВАЯ ЧАСТЬ: результаты + график =====
        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout, stretch=4)

        # --- Результаты методов ---
        result_group = QGroupBox("Значение полинома в точке x*")
        rg_layout = QGridLayout(result_group)
        rg_layout.setHorizontalSpacing(8)
        rg_layout.setVerticalSpacing(6)

        self.le_res_lagrange = QLineEdit()
        self.le_res_newton = QLineEdit()
        self.le_res_canon = QLineEdit()

        for le in (self.le_res_lagrange, self.le_res_newton, self.le_res_canon):
            le.setReadOnly(True)

        rg_layout.addWidget(QLabel("Лагранжа:"), 0, 0)
        rg_layout.addWidget(self.le_res_lagrange, 0, 1)

        rg_layout.addWidget(QLabel("Ньютона:"), 1, 0)
        rg_layout.addWidget(self.le_res_newton, 1, 1)

        rg_layout.addWidget(QLabel("Канонический:"), 2, 0)
        rg_layout.addWidget(self.le_res_canon, 2, 1)

        right_layout.addWidget(result_group)

        # --- График ---
        graph_group = QGroupBox("График P(x) и узлов")
        gg_layout = QVBoxLayout(graph_group)

        self.graph_label = QLabel("График появится после расчёта")
        self.graph_label.setObjectName("graphLabel")
        self.graph_label.setAlignment(Qt.AlignCenter)
        self.graph_label.setMinimumHeight(260)
        gg_layout.addWidget(self.graph_label)

        legend = QLabel("Синяя линия — P(x), квадратные маркеры — табличные точки")
        legend.setAlignment(Qt.AlignCenter)
        legend.setObjectName("legendLabel")
        gg_layout.addWidget(legend)

        right_layout.addWidget(graph_group)

        # ===== Сигналы =====
        self.btn_add.clicked.connect(self.on_add_point)
        self.btn_auto.clicked.connect(self.on_auto_values)
        self.btn_delete.clicked.connect(self.on_delete_selected)
        self.btn_clear.clicked.connect(self.on_clear_all)
        self.btn_calc.clicked.connect(self.on_calculate)

        # применяем стили уже после создания всех виджетов/свойств
        self.setStyleSheet(APP_STYLES)

    # ------ ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ UI ------

    @staticmethod
    def _make_labeled_list(title: str, list_widget: QListWidget) -> QWidget:
        box = QWidget()
        layout = QVBoxLayout(box)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(title)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(list_widget)
        return box

    def _read_lists(self):
        """Считываем X и Y из QListWidget в два списка float."""
        xs, ys = [], []

        if self.list_x.count() != self.list_y.count():
            raise ValueError("Количество значений X и Y должно совпадать.")

        for i in range(self.list_x.count()):
            x_text = self.list_x.item(i).text()
            y_text = self.list_y.item(i).text()
            xs.append(float(x_text))
            ys.append(float(y_text))
        return xs, ys

    # ------ ОБРАБОТЧИКИ КНОПОК ------

    def on_add_point(self):
        try:
            x = float(self.le_x.text().replace(",", "."))
            y = float(self.le_y.text().replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректные числа x и y.")
            return

        self.list_x.addItem(QListWidgetItem(str(x)))
        self.list_y.addItem(QListWidgetItem(str(y)))
        self.le_x.clear()
        self.le_y.clear()

    def on_auto_values(self):
        """Заполняем табличные значения из условия задачи."""
        self.list_x.clear()
        self.list_y.clear()

        xs = [-1.0, -0.5, 0.0, 0.5, 1.0, 1.5]
        ys = [-2.0, 0.0, 1.0, 3.5, 4.0, 3.5]

        for x, y in zip(xs, ys):
            self.list_x.addItem(QListWidgetItem(str(x)))
            self.list_y.addItem(QListWidgetItem(str(y)))

    def on_delete_selected(self):
        row = self.list_x.currentRow()
        if row < 0:
            QMessageBox.information(self, "Удаление", "Выберите строку в списке X.")
            return

        self.list_x.takeItem(row)
        self.list_y.takeItem(row)

    def on_clear_all(self):
        self.list_x.clear()
        self.list_y.clear()
        self.le_res_lagrange.clear()
        self.le_res_newton.clear()
        self.le_res_canon.clear()
        self.graph_label.setText("График появится после расчёта")
        self.graph_label.setPixmap(QPixmap())

    def on_calculate(self):
        # читаем x*
        try:
            x_eval = float(self.le_x_eval.text().replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректное значение x*.")
            return

        try:
            xs, ys = self._read_lists()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))
            return

        if len(xs) < 2:
            QMessageBox.warning(self, "Ошибка", "Нужно минимум две точки для интерполяции.")
            return

        # --- вычисляем полиномы ---
        try:
            val_lagr = lagrange(x_eval, xs, ys)
            val_newt = newton_interpolation(x_eval, xs, ys)
            val_canon = canonical_polynomial(x_eval, xs, ys)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка вычислений", str(e))
            return

        self.le_res_lagrange.setText(f"{val_lagr:.6f}")
        self.le_res_newton.setText(f"{val_newt:.6f}")
        self.le_res_canon.setText(f"{val_canon:.6f}")

        # --- строим график ---
        try:
            img_path = plot_graph(xs, ys, title="P(x) и табличные точки")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка графика", str(e))
            return

        if img_path and Path(img_path).exists():
            pixmap = QPixmap(img_path)
            scaled = pixmap.scaled(
                self.graph_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self.graph_label.setPixmap(scaled)
            self.graph_label.setText("")
        else:
            QMessageBox.warning(self, "График", "Не удалось загрузить изображение графика.")


def main():
    app = QApplication(sys.argv)
    window = PolyWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
