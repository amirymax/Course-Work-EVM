from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
import subprocess
import sys
import os

class MainMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Курсовая Работа - Меню")
        self.setFixedSize(600, 350)
        self.setStyleSheet("""
            QWidget {
                background-color: #e2e8f0;
            }
            QPushButton {
                background-color: #fef9c3;
                border: 2px solid #d4d4d4;
                border-radius: 6px;
                font-size: 18px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #fde68a;
            }
        """)

        title = QLabel("Выберите модуль")
        title.setFont(QFont("Arial", 20))
        title.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(title)

        grid = QHBoxLayout()

        left = QVBoxLayout()
        right = QVBoxLayout()

        btn_integrals = QPushButton("Интегралы")
        btn_equations = QPushButton("Уравнения")
        btn_poly = QPushButton("Полиномы")

        btn_lsm = QPushButton("МНК")
        btn_mkr = QPushButton("МКР")
        btn_author = QPushButton("От автора")

        btn_integrals.clicked.connect(lambda: self.open_module("integrals/main.py"))
        btn_equations.clicked.connect(lambda: self.open_module("equations/main.py"))
        btn_poly.clicked.connect(lambda: self.open_module("polynomials/main.py"))
        btn_lsm.clicked.connect(lambda: self.open_module("lsm/main.py"))
        btn_mkr.clicked.connect(lambda: self.open_module("differential/main.py"))
        btn_author.clicked.connect(self.show_author)

        left.addWidget(btn_integrals)
        left.addWidget(btn_equations)
        left.addWidget(btn_poly)

        right.addWidget(btn_lsm)
        right.addWidget(btn_mkr)
        right.addWidget(btn_author)

        grid.addLayout(left)
        grid.addLayout(right)

        layout.addLayout(grid)
        self.setLayout(layout)

    def open_module(self, path):
        abs_path = os.path.join(os.getcwd(), path)
        subprocess.Popen([sys.executable, abs_path])

    def show_author(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Об авторе")

        msg.setStyleSheet("""
            QMessageBox {
                background-color: #f1f5f9;
                font-size: 16px;
            }
            QLabel {
                color: #1e293b;
                font-size: 16px;
            }
            QPushButton {
                background-color: #e2e8f0;
                padding: 6px 16px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #cbd5e1;
            }
        """)

        msg.setText(
            "📘 <b>Информация об авторе</b><br><br>"
            "<b>Автор:</b> Зикрулло Амири<br>"
            "<b>Группа:</b> ПИ<br>"
            "<b>Год разработки:</b> 2025<br><br>"
            "Данный программный комплекс создан в рамках курсовой практики "
            "по дисциплине «Программирование для ЭВМ» и предназначен для учебных и демонстрационных целей.<br><br>"
            "© Зикрулло Амири, 2025"
        )

        msg.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec())
