"""
Визуализация вероятностей p_i(t) в переходном режиме.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path
from colorama import Fore, Style


def plot_probabilities_over_time(times, probabilities, steady_state=None, output_file="output_charts/probabilities_over_time.png"):
    """
    Строит график всех 5 вероятностей p_i(t) как функции времени.

    Args:
        times: array времён t_k
        probabilities: array векторов вероятностей P_k (num_steps x 5)
        steady_state: dict со значениями предельных вероятностей (опционально)
        output_file: путь для сохранения графика
    """
    # Извлекаем отдельные вероятности
    p1 = probabilities[:, 0]
    p2 = probabilities[:, 1]
    p3 = probabilities[:, 2]
    p4 = probabilities[:, 3]
    p5 = probabilities[:, 4]

    # Создаём фигуру
    fig, ax = plt.subplots(figsize=(14, 8), dpi=150)

    # Цвета для вероятностей (используем colormap)
    colors = plt.cm.tab10(np.linspace(0, 1, 5))

    # Строим кривые вероятностей
    line_width = 2.5
    ax.plot(times, p1, color=colors[0], linewidth=line_width, label='p₁(t)', alpha=0.8)
    ax.plot(times, p2, color=colors[1], linewidth=line_width, label='p₂(t)', alpha=0.8)
    ax.plot(times, p3, color=colors[2], linewidth=line_width, label='p₃(t)', alpha=0.8)
    ax.plot(times, p4, color=colors[3], linewidth=line_width, label='p₄(t)', alpha=0.8)
    ax.plot(times, p5, color=colors[4], linewidth=line_width, label='p₅(t)', alpha=0.8)

    # Если есть предельные вероятности, показываем их горизонтальными линиями
    if steady_state is not None:
        p_steady = steady_state['probabilities']
        linestyles = ['--', '-.', ':', '--', '-.']
        for i, (p_s, color) in enumerate(zip(p_steady, colors)):
            ax.axhline(y=p_s, color=color, linestyle=linestyles[i], linewidth=1.5,
                       alpha=0.5, label=f'p*₍{i+1}₎ = {p_s:.4f}')

    # Форматирование графика
    ax.set_xlabel('Время t', fontsize=12, fontweight='bold')
    ax.set_ylabel('Вероятность p_i(t)', fontsize=12, fontweight='bold')
    ax.set_title('Вероятности состояний в переходном режиме', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax.set_xlim(left=0)
    ax.set_ylim([-0.05, 1.05])

    # Легенда
    ax.legend(loc='upper right', fontsize=10, framealpha=0.95)

    # Сохранение
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight', dpi=150)
    plt.close()

    return str(output_path)


def plot_single_probability(times, probability, state_name, output_file=None):
    """
    Строит график одной вероятности.

    Args:
        times: array времён
        probability: array значений вероятности
        state_name: имя состояния (например, "S₁")
        output_file: путь для сохранения (опционально)

    Returns:
        путь к сохраненному файлу или None
    """
    fig, ax = plt.subplots(figsize=(12, 6), dpi=100)

    ax.plot(times, probability, linewidth=2.5, color='steelblue', label=f'p({state_name})')
    ax.fill_between(times, probability, alpha=0.3, color='steelblue')

    ax.set_xlabel('Время t', fontsize=11)
    ax.set_ylabel(f'p({state_name})', fontsize=11)
    ax.set_title(f'Вероятность состояния {state_name}', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)

    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
        return str(output_path)
    else:
        plt.show()
        return None


def print_plot_success(filepath):
    """Выводит сообщение об успешном сохранении графика."""
    print(f"{Fore.GREEN}✓ График сохранён: {filepath}{Style.RESET_ALL}")
