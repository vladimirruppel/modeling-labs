"""
Модуль для визуализации результатов СМО.
Генерирует графики и диаграммы для сравнения конфигураций.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams
import numpy as np

# Установка русского шрифта
rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
rcParams['axes.unicode_minus'] = False

# Попытка загрузить поддержку русского шрифта
import matplotlib
try:
    matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']
except:
    pass


def plot_variant_18_comparison(results, econ_results, output_path='output/variant_18_comparison.png'):
    """
    Создает сравнительный график трех конфигураций Варианта 18.

    Args:
        results: список словарей с результатами расчетов для трех конфигураций
        econ_results: список словарей с экономическими результатами
        output_path: путь для сохранения графика
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Вариант 18: Предприятие быстрого питания - Сравнение конфигураций',
                 fontsize=16, fontweight='bold')

    configs = ['Конфиг 1\n(1 служащий)', 'Конфиг 2\n(2 служащих)', 'Конфиг 3\n(2 канала)']
    colors = ['#2ecc71', '#f39c12', '#e74c3c']

    # График 1: Очередь и время ожидания
    ax1 = axes[0, 0]
    queue_lengths = [r['avg_queue_length'] for r in results]
    wait_times = [r['avg_wait_time'] for r in results]

    x = np.arange(len(configs))
    width = 0.35

    bars1 = ax1.bar(x - width/2, queue_lengths, width, label='Средняя длина очереди (машины)', color='#3498db', alpha=0.8)
    ax1_twin = ax1.twinx()
    bars2 = ax1_twin.bar(x + width/2, wait_times, width, label='Время ожидания (мин)', color='#e74c3c', alpha=0.8)

    ax1.set_xlabel('Конфигурация', fontweight='bold')
    ax1.set_ylabel('Длина очереди (машины)', fontweight='bold', color='#3498db')
    ax1_twin.set_ylabel('Время ожидания (минуты)', fontweight='bold', color='#e74c3c')
    ax1.set_title('Показатели качества обслуживания', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(configs)
    ax1.grid(axis='y', alpha=0.3)

    # Легенда
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_twin.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    # График 2: Экономические показатели (затраты vs доход vs прибыль)
    ax2 = axes[0, 1]
    salary_costs = [e['salary_costs'] for e in econ_results]
    channel_costs = [e['channel_costs'] for e in econ_results]
    revenue = [e['revenue'] for e in econ_results]
    profit = [e['profit'] for e in econ_results]

    x = np.arange(len(configs))
    width = 0.2

    bars_salary = ax2.bar(x - 1.5*width, salary_costs, width, label='Зарплата', color='#3498db', alpha=0.8)
    bars_channel = ax2.bar(x - 0.5*width, channel_costs, width, label='Стоимость каналов', color='#9b59b6', alpha=0.8)
    bars_revenue = ax2.bar(x + 0.5*width, revenue, width, label='Доход', color='#2ecc71', alpha=0.8)
    bars_profit = ax2.bar(x + 1.5*width, profit, width, label='Прибыль', color='#f39c12', alpha=0.8)

    ax2.set_xlabel('Конфигурация', fontweight='bold')
    ax2.set_ylabel('Сумма (руб/час)', fontweight='bold')
    ax2.set_title('Экономический анализ', fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(configs)
    ax2.legend(loc='upper right')
    ax2.grid(axis='y', alpha=0.3)
    ax2.axhline(y=0, color='k', linestyle='-', linewidth=0.5)

    # Добавляем значения на столбцы прибыли
    for i, (bar, val) in enumerate(zip(bars_profit, profit)):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(val):,}',
                ha='center', va='bottom' if height > 0 else 'top', fontweight='bold', fontsize=9)

    # График 3: Прибыль
    ax3 = axes[1, 0]
    profits = [e['profit'] for e in econ_results]
    roi = [e['roi'] for e in econ_results]

    bars = ax3.bar(configs, profits, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

    # Цвета в зависимости от значения
    for bar, profit in zip(bars, profits):
        if profit > 0:
            bar.set_color('#2ecc71')
        elif profit == 0:
            bar.set_color('#95a5a6')
        else:
            bar.set_color('#e74c3c')

    ax3.set_ylabel('Прибыль (руб/час)', fontweight='bold')
    ax3.set_title('Сравнение прибыли', fontweight='bold')
    ax3.grid(axis='y', alpha=0.3)
    ax3.axhline(y=0, color='k', linestyle='-', linewidth=1)

    # Добавляем значения на столбцы
    for bar, val in zip(bars, profits):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(val):,}',
                ha='center', va='bottom' if height > 0 else 'top', fontweight='bold', fontsize=11)

    # График 4: ROI процент
    ax4 = axes[1, 1]
    bars = ax4.bar(configs, roi, color=['#2ecc71', '#f39c12', '#e74c3c'], alpha=0.8, edgecolor='black', linewidth=1.5)

    ax4.set_ylabel('ROI (%)', fontweight='bold')
    ax4.set_title('Рентабельность инвестиций', fontweight='bold')
    ax4.grid(axis='y', alpha=0.3)
    ax4.axhline(y=0, color='k', linestyle='-', linewidth=1)

    # Добавляем значения на столбцы
    for bar, val in zip(bars, roi):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.1f}%',
                ha='center', va='bottom' if height > 0 else 'top', fontweight='bold', fontsize=11)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n✓ График сохранен в: {output_path}")
    return fig


def plot_performance_metrics(results, output_path='output/performance_metrics.png'):
    """
    Создает график характеристик производительности.

    Args:
        results: список словарей с результатами расчетов
        output_path: путь для сохранения графика
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Характеристики производительности систем массового обслуживания',
                 fontsize=16, fontweight='bold')

    configs = ['Конфиг 1', 'Конфиг 2', 'Конфиг 3']
    colors = ['#2ecc71', '#f39c12', '#e74c3c']

    # График 1: P0 (вероятность свободного канала)
    ax1 = axes[0, 0]
    p0_values = [r['p0'] for r in results]
    bars = ax1.bar(configs, p0_values, color=colors, alpha=0.8)
    ax1.set_ylabel('P₀ (вероятность)', fontweight='bold')
    ax1.set_title('P₀: Вероятность того, что система свободна', fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    ax1.set_ylim(0, 1)

    for bar, val in zip(bars, p0_values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.4f}', ha='center', va='bottom', fontweight='bold')

    # График 2: Среднее число заявок в системе
    ax2 = axes[0, 1]
    system_length = [r.get('avg_system_length', r.get('avg_queue_length', 0) + 1) for r in results]
    bars = ax2.bar(configs, system_length, color=colors, alpha=0.8)
    ax2.set_ylabel('Число машин', fontweight='bold')
    ax2.set_title('Среднее число заявок в системе', fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)

    for bar, val in zip(bars, system_length):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f}', ha='center', va='bottom', fontweight='bold')

    # График 3: Время в системе
    ax3 = axes[1, 0]
    system_time = [r['avg_system_time'] for r in results]
    bars = ax3.bar(configs, system_time, color=colors, alpha=0.8)
    ax3.set_ylabel('Время (минуты)', fontweight='bold')
    ax3.set_title('Среднее время пребывания в системе', fontweight='bold')
    ax3.grid(axis='y', alpha=0.3)

    for bar, val in zip(bars, system_time):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f}', ha='center', va='bottom', fontweight='bold')

    # График 4: Параметр ρ
    ax4 = axes[1, 1]
    rho_values = [r['rho'] for r in results]
    bars = ax4.bar(configs, rho_values, color=colors, alpha=0.8)
    ax4.set_ylabel('ρ (коэффициент загрузки)', fontweight='bold')
    ax4.set_title('Параметр ρ = λ/μ', fontweight='bold')
    ax4.grid(axis='y', alpha=0.3)
    ax4.axhline(y=1.0, color='r', linestyle='--', linewidth=2, label='Граница стабильности')
    ax4.legend()

    for bar, val in zip(bars, rho_values):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.4f}', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ График сохранен в: {output_path}")
    return fig


def show_graphs():
    """
    Интерактивно отображает графики.
    """
    try:
        plt.show()
    except Exception as e:
        print(f"Note: Could not display graphs interactively: {e}")
        print("Graphs have been saved to the output/ directory")
