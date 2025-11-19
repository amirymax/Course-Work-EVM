import os
import tempfile
from typing import Sequence, Tuple

import matplotlib.pyplot as plt


def plot_solution(xs: Sequence[float],
                  ys: Sequence[float],
                  filename: str | None = None) -> str:
    """
    Рисует график численного решения.
    xs, ys – массивы узлов и значений y(x).
    Возвращает путь к сохранённому изображению.
    """

    if len(xs) != len(ys):
        raise ValueError("xs и ys должны иметь одинаковую длину")

    # Файл по умолчанию во временной папке
    if filename is None:
        tmp_dir = tempfile.gettempdir()
        filename = os.path.join(tmp_dir, "mkr_graph.png")

    fig, ax = plt.subplots(figsize=(5, 4), dpi=100)

    # Линия между узлами (аналог гладкой линии в Excel)
    ax.plot(xs, ys, linewidth=2.0)

    # Квадратные маркеры в самих узлах
    ax.scatter(xs, ys, marker="s", s=40)

    ax.set_title("Численное решение задачи")
    ax.set_xlabel("x")
    ax.set_ylabel("y(x)")
    ax.grid(True)

    fig.tight_layout()
    fig.savefig(filename)
    plt.close(fig)

    return filename
