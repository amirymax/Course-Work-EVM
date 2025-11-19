import os
import tempfile
import matplotlib.pyplot as plt


def plot_graph(xs, ys, title="Graph") -> str:
    """
    Строит график по массивам xs и ys и сохраняет его в PNG-файл.

    :param xs: список/массив значений X
    :param ys: список/массив значений Y
    :param title: заголовок графика
    :return: полный путь к сохранённому изображению
    """
    # создаём фигуру
    fig, ax = plt.subplots()

    # основная линия (интерполяционный полином)
    ax.plot(xs, ys, linewidth=1.8, label="P(x)")

    # маркеры исходных точек
    ax.scatter(xs, ys, marker="s", label="узлы")

    # оси и заголовок
    ax.set_xlabel("X")
    ax.set_ylabel("F(X)")
    ax.set_title(title)
    ax.grid(True)
    ax.legend()

    # сохраняем во временный файл
    tmp_dir = tempfile.gettempdir()
    file_path = os.path.join(tmp_dir, "interp_graph.png")
    fig.savefig(file_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return file_path
