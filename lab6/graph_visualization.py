"""
Визуализация графа состояний марковского процесса.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Circle
import numpy as np
from pathlib import Path
from colorama import Fore, Style


def draw_state_graph(Lambda, title="Граф состояний", output_file=None):
    """
    Рисует граф состояний марковской системы.

    Args:
        Lambda: матрица интенсивностей (5x5)
        title: заголовок графика
        output_file: путь для сохранения (опционально)

    Returns:
        путь к сохраненному файлу или None
    """
    fig, ax = plt.subplots(figsize=(12, 10), dpi=150)

    # Координаты вершин (5 состояний по кругу)
    n_states = 5
    angles = np.linspace(0, 2*np.pi, n_states, endpoint=False)
    radius = 2
    positions = {}
    for i, angle in enumerate(angles):
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        positions[i] = (x, y)

    # Толщина линий пропорциональна интенсивности
    # Получаем максимум по модулю среди недиагональных элементов
    Lambda_copy = Lambda.copy()
    np.fill_diagonal(Lambda_copy, 0)
    max_lambda = np.max(np.abs(Lambda_copy))
    if max_lambda == 0:
        max_lambda = 1  # Предотвращение деления на ноль

    # Рисуем вершины (состояния)
    for state_id, (x, y) in positions.items():
        circle = Circle((x, y), radius=0.3, color='lightblue', ec='navy', linewidth=2.5, zorder=3)
        ax.add_patch(circle)
        ax.text(x, y, f'S{state_id+1}', fontsize=14, fontweight='bold',
                ha='center', va='center', zorder=4)

    # Рисуем рёбра (переходы)
    tolerance = 1e-10
    for i in range(n_states):
        for j in range(n_states):
            if i == j or abs(Lambda[i][j]) < tolerance:
                continue

            # Интенсивность перехода
            intensity = Lambda[i][j]

            # Координаты начала и конца стрелки
            x1, y1 = positions[i]
            x2, y2 = positions[j]

            # Уменьшаем длину стрелки, чтобы она не выходила из кружка
            dx = x2 - x1
            dy = y2 - y1
            dist = np.sqrt(dx**2 + dy**2)

            if dist > 0:
                dx_norm = dx / dist
                dy_norm = dy / dist

                # Начало стрелки (на границе круга S_i)
                start_x = x1 + 0.3 * dx_norm
                start_y = y1 + 0.3 * dy_norm

                # Конец стрелки (на границе круга S_j)
                end_x = x2 - 0.3 * dx_norm
                end_y = y2 - 0.3 * dy_norm

                # Толщина стрелки
                arrow_width = 1.5 + 2.5 * (abs(intensity) / max_lambda)

                # Цвет в зависимости от интенсивности
                if intensity > 0:
                    color = 'darkgreen'
                else:
                    color = 'darkred'

                # Рисуем стрелку
                arrow = FancyArrowPatch(
                    (start_x, start_y), (end_x, end_y),
                    arrowstyle='->', mutation_scale=20, linewidth=arrow_width,
                    color=color, alpha=0.7, zorder=2
                )
                ax.add_patch(arrow)

                # Добавляем подпись с интенсивностью
                mid_x = (start_x + end_x) / 2
                mid_y = (start_y + end_y) / 2

                # Смещение подписи перпендикулярно стрелке
                offset = 0.25
                perp_x = -dy_norm * offset
                perp_y = dx_norm * offset

                ax.text(mid_x + perp_x, mid_y + perp_y, f'λ={intensity:.0f}',
                        fontsize=9, ha='center', va='center',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

    # Форматирование осей
    ax.set_xlim(-3.5, 3.5)
    ax.set_ylim(-3.5, 3.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

    # Сохранение
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, bbox_inches='tight', dpi=150, facecolor='white')
        plt.close()
        return str(output_path)
    else:
        plt.show()
        return None


def draw_comparison_graphs(Lambda_original, Lambda_modified=None,
                           output_file_orig="output_charts/graph_original.png",
                           output_file_mod="output_charts/graph_modified.png"):
    """
    Рисует исходный граф и модифицированный (если задан).

    Args:
        Lambda_original: исходная матрица интенсивностей
        Lambda_modified: модифицированная матрица (опционально)
        output_file_orig: путь для исходного графика
        output_file_mod: путь для модифицированного графика

    Returns:
        tuple (path_original, path_modified или None)
    """
    path_orig = draw_state_graph(Lambda_original,
                                 title="Исходный граф состояний (вариант 18)",
                                 output_file=output_file_orig)

    path_mod = None
    if Lambda_modified is not None:
        path_mod = draw_state_graph(Lambda_modified,
                                    title="Модифицированный граф (неэргодичный)",
                                    output_file=output_file_mod)

    return path_orig, path_mod


def print_graph_success(filepath):
    """Выводит сообщение об успешном сохранении графика."""
    print(f"{Fore.GREEN}✓ Граф состояний сохранён: {filepath}{Style.RESET_ALL}")
