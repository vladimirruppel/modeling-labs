"""Визуализация расписания обработки деталей (диаграммы Ганта)"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import numpy as np


def draw_gantt_chart(details, sequence, times, result, title, filename=None):
    """
    Рисование диаграммы Ганта для последовательности обработки.

    Args:
        details: список номеров деталей
        sequence: последовательность запуска
        times: матрица времен обработки
        result: результаты расчета матричного метода
        title: заголовок диаграммы
        filename: имя файла для сохранения (если None, только показывает)
    """
    T = result['T']
    num_machines = len(times[0])
    detail_index = {details[i]: i for i in range(len(details))}

    # Создаем фигуру
    fig, ax = plt.subplots(figsize=(16, 10))

    # Цвета для каждой детали
    colors = plt.cm.tab20(np.linspace(0, 1, len(sequence)))
    detail_colors = {sequence[i]: colors[i] for i in range(len(sequence))}

    # Рисуем операции для каждой машины
    for machine_idx in range(num_machines):
        y_pos = num_machines - machine_idx  # машины сверху вниз

        for i, detail in enumerate(sequence):
            detail_idx = detail_index[detail]
            t_ij = times[detail_idx][machine_idx]

            if t_ij == 0:
                # Пропускаем нулевые времена
                continue

            # Время начала операции
            if i == 0:
                prev_detail_end = 0
            else:
                prev_detail_end = T[i - 1][machine_idx]

            if machine_idx == 0:
                prev_machine_end = 0
            else:
                prev_machine_end = T[i][machine_idx - 1]

            start_time = max(prev_detail_end, prev_machine_end)
            end_time = start_time + t_ij

            # Рисуем прямоугольник для операции
            rect = Rectangle(
                (start_time, y_pos - 0.8),
                t_ij,
                0.6,
                linewidth=1,
                edgecolor='black',
                facecolor=detail_colors[detail],
                alpha=0.7
            )
            ax.add_patch(rect)

            # Добавляем текст с номером детали и временем
            ax.text(
                start_time + t_ij / 2,
                y_pos - 0.5,
                f'{detail}',
                ha='center',
                va='center',
                fontsize=9,
                fontweight='bold'
            )

        # Рисуем простой машины (если есть)
        if i > 0:
            for i_idle, detail in enumerate(sequence[:-1]):
                detail_idx = detail_index[detail]
                t_ij = times[detail_idx][machine_idx]

                if t_ij == 0:
                    continue

                if machine_idx == 0:
                    prev_machine_end = 0
                else:
                    prev_machine_end = T[i_idle][machine_idx - 1]

                current_end = T[i_idle][machine_idx]

                if prev_machine_end < current_end:
                    # Есть простой
                    idle_time = prev_machine_end - T[i_idle - 1][machine_idx] if i_idle > 0 else 0

                    if idle_time > 0:
                        idle_rect = Rectangle(
                            (T[i_idle - 1][machine_idx] if i_idle > 0 else 0, y_pos - 0.8),
                            idle_time,
                            0.6,
                            linewidth=1,
                            edgecolor='gray',
                            facecolor='yellow',
                            alpha=0.3,
                            hatch='///'
                        )
                        ax.add_patch(idle_rect)

    # Настройки осей
    ax.set_ylim(0.5, num_machines + 0.5)
    ax.set_xlim(0, result['T_cycle'] + 5)

    ax.set_xlabel('Время', fontsize=12, fontweight='bold')
    ax.set_ylabel('Станки', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold')

    # Установка меток на оси Y
    ax.set_yticks(range(1, num_machines + 1))
    ax.set_yticklabels([f'{i}' for i in range(1, num_machines + 1)])

    # Сетка
    ax.grid(True, axis='x', alpha=0.3)

    # Легенда
    legend_elements = [
        mpatches.Patch(facecolor=detail_colors[detail], edgecolor='black', label=f'Деталь {detail}')
        for detail in sequence
    ]
    ax.legend(handles=legend_elements, loc='upper right', ncol=min(4, len(sequence)))

    # Добавляем информацию о времени цикла
    info_text = f"Время цикла: {result['T_cycle']}\nПосл-ть: {' → '.join(map(str, sequence))}"
    ax.text(
        0.02,
        0.98,
        info_text,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    )

    plt.tight_layout()

    if filename:
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"Диаграмма сохранена в: {filename}")
        plt.close()
    else:
        plt.show()


def save_gantt_chart(details, sequence, times, result, title, filename):
    """Сохранение диаграммы Ганта в файл"""
    draw_gantt_chart(details, sequence, times, result, title, filename)
