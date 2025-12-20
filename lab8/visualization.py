# -*- coding: utf-8 -*-
"""
Визуализация результатов симуляции.

Создание 6 типов графиков для анализа и отчётов.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
from stats_aggregation import MultiRealizationStatistics, RealizationStatistics


# Настройка шрифтов для поддержки русского языка
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Liberation Sans', 'Arial']
plt.rcParams['axes.unicode_minus'] = False


def ensure_output_dir() -> Path:
    """Создать директорию output если её нет."""
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


def plot_state_probabilities_comparison(theoretical: Dict[int, float],
                                       simulated: Dict[int, float],
                                       std_deviations: Dict[int, float],
                                       config_desc: str = "",
                                       output_path: Optional[Path] = None) -> str:
    """
    График 1: Сравнение вероятностей состояний (теория vs симуляция).

    Args:
        theoretical: Теоретические вероятности
        simulated: Симуляционные вероятности
        std_deviations: Стандартные отклонения
        config_desc: Описание конфигурации
        output_path: Путь для сохранения

    Returns:
        Путь сохранённого файла
    """
    output_dir = ensure_output_dir()
    if output_path is None:
        output_path = output_dir / "01_state_probabilities_comparison.png"

    fig, ax = plt.subplots(figsize=(12, 6))

    states = sorted(set(theoretical.keys()) | set(simulated.keys()))[:15]

    x = np.arange(len(states))
    width = 0.35

    theory_vals = [theoretical.get(s, 0) for s in states]
    sim_vals = [simulated.get(s, 0) for s in states]
    errors = [std_deviations.get(s, 0) for s in states]

    ax.bar(x - width/2, theory_vals, width, label='Теория', color='steelblue', alpha=0.8)
    ax.bar(x + width/2, sim_vals, width, label='Симуляция', color='coral',
           alpha=0.8, yerr=errors, capsize=5)

    ax.set_xlabel('Состояние системы (n)', fontsize=12)
    ax.set_ylabel('Вероятность p_n', fontsize=12)
    ax.set_title(f'Сравнение вероятностей состояний\n{config_desc}', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels([f'p_{s}' for s in states])
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    return str(output_path)


def plot_system_timeline(state_history: Dict[int, float],
                        max_time: float = 100,
                        n_channels: int = 1,
                        output_path: Optional[Path] = None) -> str:
    """
    График 2: Временная диаграмма состояний системы.

    Args:
        state_history: История времён в каждом состоянии
        max_time: Максимальное время для отображения
        n_channels: Число каналов
        output_path: Путь для сохранения

    Returns:
        Путь сохранённого файла
    """
    output_dir = ensure_output_dir()
    if output_path is None:
        output_path = output_dir / "02_system_timeline.png"

    fig, ax = plt.subplots(figsize=(14, 6))

    states = sorted(state_history.keys())
    cumulative_time = 0
    colors = plt.cm.tab20(np.linspace(0, 1, len(states)))

    for i, state in enumerate(states):
        duration = state_history[state]
        if cumulative_time < max_time:
            width = min(duration, max_time - cumulative_time)
            ax.barh(0, width, left=cumulative_time, height=0.6,
                   label=f'Состояние {state}', color=colors[i], alpha=0.8)
            cumulative_time += width

    ax.set_xlabel('Время (мин)', fontsize=12)
    ax.set_title(f'Временная диаграмма состояний системы (первые {max_time} мин)',
                fontsize=14)
    ax.set_yticks([])
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=9)
    ax.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    return str(output_path)


def plot_time_distributions(wait_times: List[float],
                           service_times: List[float],
                           system_times: List[float],
                           output_path: Optional[Path] = None) -> str:
    """
    График 3: Гистограммы распределений времён.

    Args:
        wait_times: Времена ожидания
        service_times: Времена обслуживания
        system_times: Времена в системе
        output_path: Путь для сохранения

    Returns:
        Путь сохранённого файла
    """
    output_dir = ensure_output_dir()
    if output_path is None:
        output_path = output_dir / "03_time_distributions.png"

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    # Время ожидания
    if wait_times:
        axes[0].hist(wait_times, bins=30, color='steelblue', alpha=0.7, edgecolor='black')
        axes[0].axvline(np.mean(wait_times), color='red', linestyle='--', linewidth=2,
                       label=f'Среднее = {np.mean(wait_times):.2f}')
        axes[0].set_xlabel('Время (мин)', fontsize=11)
        axes[0].set_ylabel('Частота', fontsize=11)
        axes[0].set_title('Распределение времени ожидания', fontsize=12)
        axes[0].legend()
        axes[0].grid(alpha=0.3)

    # Время обслуживания
    if service_times:
        axes[1].hist(service_times, bins=30, color='coral', alpha=0.7, edgecolor='black')
        axes[1].axvline(np.mean(service_times), color='red', linestyle='--', linewidth=2,
                       label=f'Среднее = {np.mean(service_times):.2f}')
        axes[1].set_xlabel('Время (мин)', fontsize=11)
        axes[1].set_ylabel('Частота', fontsize=11)
        axes[1].set_title('Распределение времени обслуживания', fontsize=12)
        axes[1].legend()
        axes[1].grid(alpha=0.3)

    # Время в системе
    if system_times:
        axes[2].hist(system_times, bins=30, color='lightgreen', alpha=0.7, edgecolor='black')
        axes[2].axvline(np.mean(system_times), color='red', linestyle='--', linewidth=2,
                       label=f'Среднее = {np.mean(system_times):.2f}')
        axes[2].set_xlabel('Время (мин)', fontsize=11)
        axes[2].set_ylabel('Частота', fontsize=11)
        axes[2].set_title('Распределение времени в системе', fontsize=12)
        axes[2].legend()
        axes[2].grid(alpha=0.3)

    plt.suptitle('Распределения времён в системе', fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    return str(output_path)


def plot_configuration_comparison(configs_results: List[Dict],
                                 output_path: Optional[Path] = None) -> str:
    """
    График 4: Сравнение трёх конфигураций.

    Args:
        configs_results: Список результатов для каждой конфигурации
        output_path: Путь для сохранения

    Returns:
        Путь сохранённого файла
    """
    output_dir = ensure_output_dir()
    if output_path is None:
        output_path = output_dir / "04_configuration_comparison.png"

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    config_ids = [f"Config {cfg.get('config_id', i+1)}" for i, cfg in enumerate(configs_results)]

    # Средняя длина очереди
    queue_lengths = [cfg.get('characteristics', {}).get('queue_length', {}).get('simulated', 0)
                    for cfg in configs_results]
    axes[0].bar(config_ids, queue_lengths, color='steelblue', alpha=0.7, edgecolor='black')
    axes[0].set_ylabel('Длина очереди', fontsize=11)
    axes[0].set_title('Средняя длина очереди r̄', fontsize=12)
    axes[0].grid(axis='y', alpha=0.3)

    # Среднее время ожидания
    wait_times = [cfg.get('characteristics', {}).get('wait_time', {}).get('simulated', 0)
                 for cfg in configs_results]
    axes[1].bar(config_ids, wait_times, color='coral', alpha=0.7, edgecolor='black')
    axes[1].set_ylabel('Время (мин)', fontsize=11)
    axes[1].set_title('Среднее время ожидания t̄_ож', fontsize=12)
    axes[1].grid(axis='y', alpha=0.3)

    # Пропускная способность
    throughputs = [cfg.get('characteristics', {}).get('absolute_throughput', {}).get('simulated', 0)
                  for cfg in configs_results]
    axes[2].bar(config_ids, throughputs, color='lightgreen', alpha=0.7, edgecolor='black')
    axes[2].set_ylabel('Пропускная способность', fontsize=11)
    axes[2].set_title('Абсолютная пропускная способность A', fontsize=12)
    axes[2].grid(axis='y', alpha=0.3)

    plt.suptitle('Сравнение конфигураций', fontsize=14, y=1.00)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    return str(output_path)


def plot_convergence(n_realizations_list: List[int],
                    characteristics_by_n: Dict[int, Dict],
                    theoretical_value: float,
                    characteristic_name: str = "r̄",
                    epsilon: float = 0.01,
                    output_path: Optional[Path] = None) -> str:
    """
    График 5: Анализ сходимости (влияние числа реализаций).

    Args:
        n_realizations_list: Список количеств реализаций
        characteristics_by_n: Словарь N -> результаты
        theoretical_value: Теоретическое значение характеристики
        characteristic_name: Название характеристики
        epsilon: Допустимая ошибка
        output_path: Путь для сохранения

    Returns:
        Путь сохранённого файла
    """
    output_dir = ensure_output_dir()
    if output_path is None:
        output_path = output_dir / "05_convergence_analysis.png"

    fig, ax = plt.subplots(figsize=(12, 6))

    values = [characteristics_by_n.get(n, {}).get('value', theoretical_value)
             for n in n_realizations_list]
    stds = [characteristics_by_n.get(n, {}).get('std', 0) for n in n_realizations_list]

    ax.errorbar(n_realizations_list, values, yerr=stds, fmt='o-', linewidth=2,
               markersize=8, capsize=5, label='Симуляция', color='steelblue')

    ax.axhline(theoretical_value, color='red', linestyle='--', linewidth=2,
              label=f'Теория = {theoretical_value:.4f}')

    # Область допуска
    upper_bound = theoretical_value * (1 + epsilon)
    lower_bound = theoretical_value * (1 - epsilon)
    ax.fill_between(n_realizations_list, lower_bound, upper_bound, alpha=0.2,
                   color='green', label=f'Допуск ±{epsilon*100:.0f}%')

    ax.set_xlabel('Число реализаций (N)', fontsize=12)
    ax.set_ylabel(f'Значение {characteristic_name}', fontsize=12)
    ax.set_title(f'Анализ сходимости: {characteristic_name}', fontsize=14)
    ax.set_xscale('log')
    ax.legend(fontsize=11)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    return str(output_path)


def plot_distribution_comparison(results_dict: Dict[str, Dict],
                                 characteristic: str = 'queue_length',
                                 output_path: Optional[Path] = None) -> str:
    """
    График 6: Сравнение различных распределений прибытия/обслуживания.

    Args:
        results_dict: Словарь распределение -> результаты
        characteristic: Характеристика для сравнения
        output_path: Путь для сохранения

    Returns:
        Путь сохранённого файла
    """
    output_dir = ensure_output_dir()
    if output_path is None:
        output_path = output_dir / "06_distribution_comparison.png"

    fig, ax = plt.subplots(figsize=(12, 6))

    distributions = list(results_dict.keys())
    values = [results_dict[d].get(characteristic, 0) for d in distributions]
    stds = [results_dict[d].get(f'{characteristic}_std', 0) for d in distributions]

    colors = ['steelblue', 'coral', 'lightgreen', 'orange']

    ax.bar(distributions, values, color=colors[:len(distributions)], alpha=0.7,
          edgecolor='black', yerr=stds, capsize=5)

    ax.set_ylabel(f'Значение {characteristic}', fontsize=12)
    ax.set_title(f'Влияние распределений на {characteristic}', fontsize=14)
    ax.grid(axis='y', alpha=0.3)

    # Добавить значения на столбцы
    for i, (dist, val) in enumerate(zip(distributions, values)):
        ax.text(i, val, f'{val:.3f}', ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    return str(output_path)


# ============================================================================
# ТЕСТИРОВАНИЕ
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("ТЕСТИРОВАНИЕ ВИЗУАЛИЗАЦИИ")
    print("=" * 70)

    output_dir = ensure_output_dir()

    # Тест 1: Сравнение вероятностей
    print("\n1. Создание графика сравнения вероятностей")
    print("-" * 70)

    theory_probs = {0: 0.200, 1: 0.160, 2: 0.128, 3: 0.102, 4: 0.082,
                   5: 0.066, 6: 0.053, 7: 0.042, 8: 0.034, 9: 0.027}
    sim_probs = {0: 0.194, 1: 0.157, 2: 0.123, 3: 0.102, 4: 0.086,
                5: 0.072, 6: 0.058, 7: 0.043, 8: 0.039, 9: 0.033}
    stds = {k: theory_probs[k] * 0.1 for k in theory_probs}

    path = plot_state_probabilities_comparison(theory_probs, sim_probs, stds,
                                              "M/M/1 (λ=0.4, μ=0.5)")
    print(f"✓ Сохранено: {path}")

    # Тест 2: Временная диаграмма
    print("\n2. Создание временной диаграммы")
    print("-" * 70)

    state_hist = {0: 2000, 1: 1500, 2: 1200, 3: 1000, 4: 800, 5: 600,
                 6: 400, 7: 200, 8: 100, 9: 50, 10: 150}

    path = plot_system_timeline(state_hist, max_time=100)
    print(f"✓ Сохранено: {path}")

    # Тест 3: Гистограммы времён
    print("\n3. Создание гистограмм распределений времён")
    print("-" * 70)

    import random
    random.seed(42)
    np.random.seed(42)

    wait_times = [abs(np.random.exponential(9.5)) for _ in range(1000)]
    service_times = [abs(np.random.exponential(2.0)) for _ in range(1000)]
    system_times = [w + s for w, s in zip(wait_times, service_times)]

    path = plot_time_distributions(wait_times, service_times, system_times)
    print(f"✓ Сохранено: {path}")

    # Тест 4: Сравнение конфигураций
    print("\n4. Создание графика сравнения конфигураций")
    print("-" * 70)

    configs = [
        {
            'config_id': 1,
            'characteristics': {
                'queue_length': {'simulated': 3.2},
                'wait_time': {'simulated': 8.0},
                'absolute_throughput': {'simulated': 0.4}
            }
        },
        {
            'config_id': 2,
            'characteristics': {
                'queue_length': {'simulated': 0.8},
                'wait_time': {'simulated': 2.0},
                'absolute_throughput': {'simulated': 0.4}
            }
        },
        {
            'config_id': 3,
            'characteristics': {
                'queue_length': {'simulated': 0.5},
                'wait_time': {'simulated': 1.25},
                'absolute_throughput': {'simulated': 0.4}
            }
        }
    ]

    path = plot_configuration_comparison(configs)
    print(f"✓ Сохранено: {path}")

    # Тест 5: Анализ сходимости
    print("\n5. Создание графика сходимости")
    print("-" * 70)

    n_list = [10, 25, 50, 100, 200, 500]
    char_by_n = {
        10: {'value': 3.5, 'std': 0.8},
        25: {'value': 3.3, 'std': 0.5},
        50: {'value': 3.25, 'std': 0.3},
        100: {'value': 3.2, 'std': 0.2},
        200: {'value': 3.18, 'std': 0.15},
        500: {'value': 3.2, 'std': 0.08}
    }

    path = plot_convergence(n_list, char_by_n, theoretical_value=3.2, epsilon=0.01)
    print(f"✓ Сохранено: {path}")

    # Тест 6: Сравнение распределений
    print("\n6. Создание графика сравнения распределений")
    print("-" * 70)

    dist_results = {
        'Exponential': {'queue_length': 3.2, 'queue_length_std': 0.2},
        'Weibull': {'queue_length': 3.1, 'queue_length_std': 0.25},
        'Gamma': {'queue_length': 3.15, 'queue_length_std': 0.22},
        'Normal': {'queue_length': 3.3, 'queue_length_std': 0.3}
    }

    path = plot_distribution_comparison(dist_results)
    print(f"✓ Сохранено: {path}")

    print("\n" + "=" * 70)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 70)
    print(f"\nВсе графики сохранены в: {output_dir}")
