# -*- coding: utf-8 -*-
"""
Валидация результатов симуляции путём сравнения с теоретическими характеристиками.

Интегрирует результаты с ЛР №7 (марковские СМО) и проверяет адекватность модели.
"""

from typing import Dict, Tuple, Optional
from stats_aggregation import MultiRealizationStatistics


class MarkovianQueueTheory:
    """
    Расчёт теоретических характеристик марковских СМО.

    Поддерживает M/M/1/∞ и M/M/n/∞ системы.
    """

    @staticmethod
    def calculate_mm1_characteristics(lambda_val: float, mu_val: float) -> Dict:
        """
        Расчёт характеристик системы M/M/1/∞.

        Args:
            lambda_val: Интенсивность поступления
            mu_val: Интенсивность обслуживания

        Returns:
            Словарь с теоретическими характеристиками
        """
        rho = lambda_val / mu_val

        if rho >= 1.0:
            return {
                'error': f'Система неустойчива: ρ = {rho:.4f} ≥ 1',
                'stable': False
            }

        # Основные характеристики
        p0 = 1.0 - rho

        # Средняя длина очереди
        avg_queue_length = (rho ** 2) / (1 - rho)

        # Среднее время ожидания
        avg_wait_time = rho / (mu_val * (1 - rho))

        # Среднее время в системе
        avg_system_time = 1.0 / (mu_val * (1 - rho))

        # Среднее число в системе
        avg_in_system = rho / (1 - rho)

        # Вероятности состояний
        probabilities = {}
        for k in range(21):  # Первые 20 состояний
            probabilities[k] = p0 * (rho ** k)

        return {
            'stable': True,
            'rho': rho,
            'p0': p0,
            'lambda': lambda_val,
            'mu': mu_val,
            'avg_queue_length': avg_queue_length,
            'avg_wait_time': avg_wait_time,
            'avg_system_time': avg_system_time,
            'avg_in_system': avg_in_system,
            'probabilities': probabilities,
            'relative_throughput': 1.0,
            'absolute_throughput': lambda_val,
            'p_rejection': 0.0
        }

    @staticmethod
    def calculate_mmn_characteristics(lambda_val: float, mu_val: float,
                                      n_channels: int) -> Dict:
        """
        Расчёт характеристик системы M/M/n/∞ (Erlang C formula).

        Args:
            lambda_val: Интенсивность поступления
            mu_val: Интенсивность обслуживания одного канала
            n_channels: Число каналов

        Returns:
            Словарь с теоретическими характеристиками
        """
        rho = lambda_val / (n_channels * mu_val)

        if rho >= 1.0:
            return {
                'error': f'Система неустойчива: ρ = {rho:.4f} ≥ 1',
                'stable': False
            }

        # Интенсивность трафика
        a = lambda_val / mu_val

        # Расчёт p0 через сумму
        p0_inv = 0.0
        factorial_n = 1
        for k in range(1, n_channels + 1):
            factorial_n *= k
            p0_inv += (a ** k) / factorial_n

        # Добавляем последний член для бесконечной очереди
        factorial_n *= n_channels
        erlang_c_numerator = (a ** n_channels) / factorial_n
        erlang_c_denominator = 1.0 - rho
        p0_inv += erlang_c_numerator / erlang_c_denominator
        p0_inv += 1.0  # член для k=0

        p0 = 1.0 / p0_inv

        # Erlang C formula (вероятность ожидания)
        pw = erlang_c_numerator * p0 / erlang_c_denominator

        # Средняя длина очереди
        avg_queue_length = (pw * rho) / (1.0 - rho)

        # Среднее время ожидания
        avg_wait_time = avg_queue_length / lambda_val

        # Среднее время в системе
        avg_system_time = avg_wait_time + 1.0 / mu_val

        # Среднее число в системе
        avg_in_system = lambda_val * avg_system_time

        # Вероятности состояний
        probabilities = {}
        for k in range(min(21, n_channels + 10)):
            if k < n_channels:
                probabilities[k] = p0 * (a ** k) / (1 if k == 0 else
                    eval('*'.join(str(i) for i in range(1, k+1))))
            else:
                factorial_n = 1
                for i in range(1, n_channels + 1):
                    factorial_n *= i
                probabilities[k] = p0 * (a ** k) / (factorial_n * (n_channels ** (k - n_channels)))

        return {
            'stable': True,
            'rho': rho,
            'p0': p0,
            'pw': pw,  # Erlang C
            'lambda': lambda_val,
            'mu': mu_val,
            'n_channels': n_channels,
            'avg_queue_length': avg_queue_length,
            'avg_wait_time': avg_wait_time,
            'avg_system_time': avg_system_time,
            'avg_in_system': avg_in_system,
            'probabilities': probabilities,
            'relative_throughput': 1.0,
            'absolute_throughput': lambda_val,
            'p_rejection': 0.0
        }


class ValidationResults:
    """Результаты валидации симуляции."""

    def __init__(self, simulated: MultiRealizationStatistics,
                 theoretical: Dict):
        """
        Args:
            simulated: Агрегированные результаты симуляции
            theoretical: Теоретические результаты
        """
        self.simulated = simulated
        self.theoretical = theoretical
        self.errors = {}
        self.characteristics_comparison = {}
        self.max_error = 0.0
        self.within_tolerance = True


def validate_simulation(simulated: MultiRealizationStatistics,
                       theoretical: Dict,
                       epsilon: float = 0.01) -> ValidationResults:
    """
    Провести валидацию результатов симуляции.

    Args:
        simulated: Агрегированные результаты симуляции
        theoretical: Теоретические результаты
        epsilon: Допустимая относительная ошибка

    Returns:
        ValidationResults с ошибками и выводами
    """
    results = ValidationResults(simulated, theoretical)

    # Проверка вероятностей состояний
    theory_probs = theoretical.get('probabilities', {})
    for state in theory_probs:
        sim_prob = simulated.avg_probabilities.get(state, 0.0)
        theory_prob = theory_probs[state]

        if theory_prob > 0:
            error = abs(sim_prob - theory_prob) / theory_prob
        else:
            error = abs(sim_prob - theory_prob)

        results.errors[f'p_{state}'] = error
        results.max_error = max(results.max_error, error)

    # Проверка основных характеристик
    characteristics = {
        'queue_length': ('avg_queue_length', 'avg_queue_length'),
        'wait_time': ('avg_wait_time', 'avg_wait_time'),
        'system_time': ('avg_system_time', 'avg_system_time'),
        'rho': (None, 'rho')
    }

    for char_name, (sim_key, theory_key) in characteristics.items():
        if theory_key in theoretical:
            theory_val = theoretical[theory_key]

            if sim_key:
                sim_val = getattr(simulated, sim_key, 0.0)
            else:
                # Для rho
                sim_lambda = simulated.avg_lambda
                sim_mu = simulated.avg_mu
                n = theoretical.get('n_channels', 1)
                sim_val = sim_lambda / (n * sim_mu) if sim_mu > 0 else 0.0

            if theory_val > 0:
                error = abs(sim_val - theory_val) / theory_val
            else:
                error = abs(sim_val - theory_val)

            results.errors[char_name] = error
            results.characteristics_comparison[char_name] = {
                'simulated': sim_val,
                'theoretical': theory_val,
                'error': error,
                'error_pct': error * 100
            }
            results.max_error = max(results.max_error, error)

    # Проверка ошибок относительно допуска
    results.within_tolerance = all(err <= epsilon for err in results.errors.values())

    return results


def compare_configurations(results_list: list, configs: list,
                          epsilon: float = 0.01) -> Dict:
    """
    Сравнить результаты симуляции для нескольких конфигураций.

    Args:
        results_list: Список ValidationResults для каждой конфигурации
        configs: Список описаний конфигураций
        epsilon: Допустимая ошибка

    Returns:
        Словарь со сравнительной статистикой
    """
    comparison = {
        'total_configs': len(results_list),
        'within_tolerance_count': 0,
        'config_results': []
    }

    for i, (result, config) in enumerate(zip(results_list, configs)):
        config_result = {
            'config_id': config.get('id', i + 1),
            'config_desc': config.get('description', ''),
            'within_tolerance': result.within_tolerance,
            'max_error': result.max_error,
            'max_error_pct': result.max_error * 100,
            'characteristics': result.characteristics_comparison
        }

        comparison['config_results'].append(config_result)

        if result.within_tolerance:
            comparison['within_tolerance_count'] += 1

    comparison['success_rate'] = (
        comparison['within_tolerance_count'] / len(results_list) * 100
        if results_list else 0.0
    )

    return comparison


# ============================================================================
# ТЕСТИРОВАНИЕ
# ============================================================================

if __name__ == '__main__':
    from simulation_engine import SimulationEngine
    from config import DistributionType
    from stats_aggregation import RealizationStatistics

    print("=" * 70)
    print("ТЕСТИРОВАНИЕ ВАЛИДАЦИИ")
    print("=" * 70)

    # Создать теоретические результаты для M/M/1
    print("\n1. Расчёт теоретических характеристик M/M/1 (λ=0.4, μ=0.5)")
    print("-" * 70)

    theory = MarkovianQueueTheory.calculate_mm1_characteristics(0.4, 0.5)
    print(f"ρ = {theory['rho']:.4f}")
    print(f"p_0 = {theory['p0']:.6f}")
    print(f"r̄ = {theory['avg_queue_length']:.4f}")
    print(f"t̄_ож = {theory['avg_wait_time']:.4f}")
    print(f"t̄_сист = {theory['avg_system_time']:.4f}")

    # Запустить 5 реализаций симуляции
    print("\n2. Запуск 5 реализаций симуляции (T=5000)")
    print("-" * 70)

    engine = SimulationEngine(
        n_channels=1,
        m_queue=None,
        lambda_param=0.4,
        mu_param=0.5,
        arrival_dist=DistributionType.EXPONENTIAL,
        service_dist=DistributionType.EXPONENTIAL,
        seed=18
    )

    realizations = []
    for i in range(5):
        result = engine.run_single_realization(T=5000)
        real_stats = RealizationStatistics.from_simulation_result(result)
        realizations.append(real_stats)

    multi_stats = MultiRealizationStatistics(N_realizations=5, realizations=realizations)
    multi_stats.compute_statistics()

    # Провести валидацию
    print("\n3. Результаты валидации")
    print("-" * 70)

    validation = validate_simulation(multi_stats, theory, epsilon=0.01)

    print(f"Максимальная ошибка: {validation.max_error:.6f} ({validation.max_error*100:.2f}%)")
    print(f"В допуске: {'ДА' if validation.within_tolerance else 'НЕТ'}")

    print(f"\nСравнение характеристик:")
    for char_name, comp in validation.characteristics_comparison.items():
        print(f"  {char_name}:")
        print(f"    Теория:   {comp['theoretical']:.6f}")
        print(f"    Симуляция: {comp['simulated']:.6f}")
        print(f"    Ошибка:   {comp['error_pct']:.2f}%")

    print("\n" + "=" * 70)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 70)
