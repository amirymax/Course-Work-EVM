from __future__ import annotations

from pathlib import Path
from typing import Sequence, Tuple

import numpy as np
import matplotlib.pyplot as plt


def draw_lsm_graph(
    x_vals: Sequence[float],
    y_vals: Sequence[float],
    lin_params: Tuple[float, float],          # (a1, b1)   для y = a1 * x + b1
    quad_params: Tuple[float, float, float],  # (a2, b2, c2) для y = a2*x^2 + b2*x + c2
    custom_params: Tuple[float, float],       # (a3, b3)   для y = a3 / x + b3
    output_path: str | Path = "lsm_graph.png",
) -> Path:
    """
    Строит график экспериментальных точек и трёх аппроксимирующих функций.
    Возвращает путь к сохранённому изображению.
    """

    x = np.asarray(x_vals, dtype=float)
    y = np.asarray(y_vals, dtype=float)

    if x.size == 0:
        raise ValueError("Список точек пуст")

    # --- разворачиваем параметры ---
    a1, b1 = lin_params
    a2, b2, c2 = quad_params
    a3, b3 = custom_params

    # --- сетка для гладких линий ---
    x_plot = np.linspace(x.min(), x.max(), 300)

    # избегаем деления на ноль в модели a/x + b
    x_plot_safe = np.where(x_plot == 0, 1e-8, x_plot)

    y_lin = a1 * x_plot + b1
    y_quad = a2 * x_plot**2 + b2 * x_plot + c2
    y_custom = a3 / x_plot_safe + b3

    # --- построение графика ---
    fig, ax = plt.subplots(figsize=(6, 4), dpi=120)

    # экспериментальные точки
    ax.scatter(x, y, marker="s", label="экспериментальные точки")

    # три аппроксимации
    ax.plot(x_plot, y_lin, label="линейная аппроксимация")
    ax.plot(x_plot, y_quad, label="квадратичная аппроксимация")
    ax.plot(x_plot, y_custom, label="аппроксимация a/x + b")

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Метод наименьших квадратов")
    ax.grid(True, linestyle="--", linewidth=0.5)
    ax.legend()

    fig.tight_layout()

    output_path = Path(output_path)
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)

    return output_path
