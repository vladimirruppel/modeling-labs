import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import os

# Словарь, чтобы цвета были постоянными для каждой детали
DETAIL_COLORS = {}
BASE_COLORS = plt.get_cmap('tab10').colors + plt.get_cmap('Set2').colors

def _get_color(detail_id):
    """Возвращает постоянный цвет для ID детали."""
    if detail_id not in DETAIL_COLORS:
        DETAIL_COLORS[detail_id] = BASE_COLORS[len(DETAIL_COLORS) % len(BASE_COLORS)]
    return DETAIL_COLORS[detail_id]

def calculate_times(sequence, num_machines):
    """
    Рассчитывает времена начала, окончания и простоев для заданной последовательности.
    Возвращает детальную временную шкалу и общее время.
    """
    timeline = []
    if num_machines == 2:
        time_a_ends, time_b_ends = 0, 0
        for detail in sequence:
            start_a = time_a_ends
            end_a = start_a + detail['a']
            start_b = max(end_a, time_b_ends)
            end_b = start_b + detail['b']
            idle_b = start_b - time_b_ends
            timeline.append({
                'id': detail['id'], 'a': detail['a'], 'b': detail['b'],
                'start_a': start_a, 'end_a': end_a,
                'start_b': start_b, 'end_b': end_b, 'idle_b': idle_b
            })
            time_a_ends, time_b_ends = end_a, end_b
        return timeline, time_b_ends

    elif num_machines == 3:
        time_a_ends, time_b_ends, time_c_ends = 0, 0, 0
        for detail in sequence:
            start_a = time_a_ends
            end_a = start_a + detail['a']
            start_b = max(end_a, time_b_ends)
            end_b = start_b + detail['b']
            start_c = max(end_b, time_c_ends)
            end_c = start_c + detail['c']
            idle_b = start_b - time_b_ends
            idle_c = start_c - time_c_ends
            timeline.append({
                'id': detail['id'], 'a': detail['a'], 'b': detail['b'], 'c': detail['c'],
                'start_a': start_a, 'end_a': end_a,
                'start_b': start_b, 'end_b': end_b,
                'start_c': start_c, 'end_c': end_c,
                'idle_b': idle_b, 'idle_c': idle_c
            })
            time_a_ends, time_b_ends, time_c_ends = end_a, end_b, end_c
        return timeline, time_c_ends

def show_gantt_chart(details_in_orig_order, sequence, title="График Ганта", filename=None):
    """
    Отображает график Ганта и опционально сохраняет его в файл.
    """
    DETAIL_COLORS.clear()
    for detail in details_in_orig_order:
        _get_color(detail['id'])

    num_machines = 3 if 'c' in sequence[0] else 2
    machines = ['A', 'B', 'C'][:num_machines]
    
    timeline, total_time = calculate_times(sequence, num_machines)

    fig_height = 2.5 + num_machines * 0.8
    fig, ax = plt.subplots(figsize=(12, fig_height))

    bar_height = 0.6
    idle_b_counter = 1
    idle_c_counter = 1

    # Рисуем операции для каждой детали
    for item in timeline:
        # Станок A
        ax.barh('A', width=item['a'], left=item['start_a'], height=bar_height, color=_get_color(item['id']), edgecolor='black', zorder=3)
        ax.text(item['start_a'] + item['a'] / 2, 'A', f"a{item['id']}", ha='center', va='center', color='white', weight='bold', fontsize=9)

        # Станок B
        ax.barh('B', width=item['b'], left=item['start_b'], height=bar_height, color=_get_color(item['id']), edgecolor='black', zorder=3)
        ax.text(item['start_b'] + item['b'] / 2, 'B', f"b{item['id']}", ha='center', va='center', color='white', weight='bold', fontsize=9)
        
        # Рисуем желтый блок простоя для станка B
        if item['idle_b'] > 0:
            idle_start_pos = item['start_b'] - item['idle_b']
            # Рисуем полупрозрачный желтый прямоугольник
            ax.barh('B', width=item['idle_b'], left=idle_start_pos, height=bar_height, color='yellow', alpha=0.5, edgecolor='gray', hatch='//', zorder=2)
            # Добавляем подпись
            ax.text(idle_start_pos + item['idle_b'] / 2, 1, f"x{idle_b_counter}", ha='center', va='top', color='black', style='italic', fontsize=8)
            idle_b_counter += 1

        # Станок C (если есть)
        if num_machines == 3:
            ax.barh('C', width=item['c'], left=item['start_c'], height=bar_height, color=_get_color(item['id']), edgecolor='black', zorder=3)
            ax.text(item['start_c'] + item['c'] / 2, 'C', f"c{item['id']}", ha='center', va='center', color='white', weight='bold', fontsize=9)
            
            # Рисуем желтый блок простоя для станка C
            if item['idle_c'] > 0:
                idle_start_pos = item['start_c'] - item['idle_c']
                ax.barh('C', width=item['idle_c'], left=idle_start_pos, height=bar_height, color='yellow', alpha=0.5, edgecolor='gray', hatch='//', zorder=2)
                ax.text(idle_start_pos + item['idle_c'] / 2, 2, f"y{idle_c_counter}", ha='center', va='top', color='black', style='italic', fontsize=8)
                idle_c_counter += 1

    # Настройка осей и легенды
    ax.set_xlabel("Время")
    ax.set_title(f"{title}\nОбщее время выполнения (T): {total_time}")
    ax.set_yticks(range(len(machines)), labels=machines)
    ax.set_xlim(0, total_time)
    ax.grid(True, axis='x', linestyle='--', linewidth=0.5, zorder=0)
    ax.invert_yaxis()

    tick_step = 1
    if total_time > 30:
        tick_step = 5
    elif total_time > 15:
        tick_step = 2

    ticks = list(np.arange(0, total_time, tick_step, dtype=int))
    if total_time not in ticks:
        ticks.append(total_time)
    
    ax.set_xticks(ticks)
    
    # Добавляем элемент "Простой" в легенду
    legend_elements = [Patch(facecolor=_get_color(d['id']), edgecolor='black', label=f"Деталь {d['id']}") for d in details_in_orig_order]
    legend_elements.append(Patch(facecolor='yellow', alpha=0.5, edgecolor='gray', hatch='//', label='Простой'))
    ax.legend(handles=legend_elements, bbox_to_anchor=(1.02, 1), loc='upper left')

    plt.tight_layout(rect=[0, 0, 0.85, 1])
    
    # Сохраняем график в файл, если указано имя файла
    if filename:
        output_dir = "output_charts"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        full_path = os.path.join(output_dir, filename)
        try:
            plt.savefig(full_path, bbox_inches='tight')
            print(f"График сохранен в файл: {full_path}")
        except Exception as e:
            print(f"Не удалось сохранить график: {e}")
    
    plt.show()
