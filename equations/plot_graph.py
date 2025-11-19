import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from PySide6.QtGui import QPixmap


def plot_function(f, a, b, root=None):
    """
    Рисует график функции f(x) на интервале [a, b] с 200 точками.
    Если root задан — добавляет красную точку в корне.
    Возвращает QPixmap, готовый для установки в QLabel.
    """

    # 1. Генерация сетки
    x = np.linspace(a, b, 200)
    y = f(x)

    # 2. Построение графика
    fig, ax = plt.subplots(figsize=(4, 3), dpi=120)
    ax.plot(x, y, label="f(x)")
    ax.set_xlabel("X")
    ax.set_ylabel("F(X)")
    ax.set_title("Equation graph")
    ax.grid(True)

    # 3. Корень, если найден
    if root is not None:
        ax.scatter([root], [f(root)], color="red", s=40, label="root")
        ax.legend()

    # 4. Сохранение в память
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)

    # 5. Конвертация в QPixmap
    pixmap = QPixmap()
    pixmap.loadFromData(buf.read())

    return pixmap
