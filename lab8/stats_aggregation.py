# -*- coding: utf-8 -*-
"""
Расчёт и агрегирование статистики по результатам симуляции.

Включает классы для хранения результатов одной реализации и
агрегирования результатов по нескольким реализациям (Монте-Карло).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import statistics as stat_module


@dataclass
class RealizationStatistics:
    """
    Статистика результатов одной реализации симуляции.

    Содержит все характеристики СМО, рассчитанные из одной реализации.
    """
    T: float                              # Интервал моделирования (минуты)
    N_arrivals: int                       # Число прибывших заявок
    N_served: int                         # Число обслуженных заявок
    N_rejected: int                       # Число отказов
    probabilities: Dict[int, float]       # Вероятности состояний p_i
    lambda_avg: float                     # Средняя интенсивность поступления λ̄
    mu_avg: float                         # Средняя интенсивность обслуживания μ̄
    p_rejection: float                    # Вероятность отказа p_отк
    relative_throughput: float            # Относительная пропускная способность q
    absolute_throughput: float            # Абсолютная пропускная способность A
    avg_busy_channels: float              # Среднее число занятых каналов k̄
    avg_queue_length: float               # Средняя длина очереди r̄
    avg_wait_time: float                  # Среднее время ожидания t̄_ож
    avg_system_time: float                # Среднее время в системе t̄_сист
    service_times: List[float] = field(default_factory=list)  # Времена обслуживания
    wait_times: List[float] = field(default_factory=list)     # Времена ожидания
    system_times: List[float] = field(default_factory=list)   # Времена в системе

    @classmethod
    def from_simulation_result(cls, result: Dict) -> 'RealizationStatistics':
        """
        Создать объект из результата simulation_engine.run_single_realization().

        Args:
            result: Словарь результатов из SimulationEngine

        Returns:
            RealizationStatistics объект
        """
        return cls(
            T=result['T'],
            N_arrivals=result['N_arrivals'],
            N_served=result['N_served'],
            N_rejected=result['N_rejected'],
            probabilities=result['probabilities'],
            lambda_avg=result['lambda_avg'],
            mu_avg=result['mu_avg'],
            p_rejection=result['p_rejection'],
            relative_throughput=result['relative_throughput'],
            absolute_throughput=result['absolute_throughput'],
            avg_busy_channels=result['avg_busy_channels'],
            avg_queue_length=result['avg_queue_length'],
            avg_wait_time=result['avg_wait_time'],
            avg_system_time=result['avg_system_time'],
            service_times=result['service_times'],
            wait_times=result['wait_times'],
            system_times=result['system_times']
        )


@dataclass
class MultiRealizationStatistics:
    """
    Агрегированная статистика по нескольким реализациям симуляции.

    Вычисляет средние значения, стандартные отклонения и доверительные интервалы
    для всех характеристик СМО по методу Монте-Карло.
    """
    N_realizations: int                             # Число реализаций
    realizations: List[RealizationStatistics]       # Все реализации

    # Средние значения характеристик
    avg_probabilities: Dict[int, float] = field(default_factory=dict)
    std_probabilities: Dict[int, float] = field(default_factory=dict)

    avg_lambda: float = 0.0                         # Среднее λ̄
    std_lambda: float = 0.0                         # Стд.откл. λ̄

    avg_mu: float = 0.0                             # Среднее μ̄
    std_mu: float = 0.0                             # Стд.откл. μ̄

    avg_p_rejection: float = 0.0                    # Среднее p_отказ
    std_p_rejection: float = 0.0                    # Стд.откл. p_отказ

    avg_absolute_throughput: float = 0.0            # Среднее A
    std_absolute_throughput: float = 0.0            # Стд.откл. A

    avg_queue_length: float = 0.0                   # Среднее r̄
    std_queue_length: float = 0.0                   # Стд.откл. r̄

    avg_wait_time: float = 0.0                      # Среднее t̄_ож
    std_wait_time: float = 0.0                      # Стд.откл. t̄_ож

    avg_system_time: float = 0.0                    # Среднее t̄_сист
    std_system_time: float = 0.0                    # Стд.откл. t̄_сист

    avg_busy_channels: float = 0.0                  # Среднее k̄
    std_busy_channels: float = 0.0                  # Стд.откл. k̄

    def compute_statistics(self) -> None:
        """
        Вычислить средние значения и стандартные отклонения по всем реализациям.
        """
        if not self.realizations:
            return

        # Вероятности состояний
        all_states = set()
        for real in self.realizations:
            all_states.update(real.probabilities.keys())

        for state in sorted(all_states):
            state_probs = [real.probabilities.get(state, 0.0) for real in self.realizations]
            self.avg_probabilities[state] = stat_module.mean(state_probs)
            if len(state_probs) > 1:
                self.std_probabilities[state] = stat_module.stdev(state_probs)
            else:
                self.std_probabilities[state] = 0.0

        # Интенсивности
        lambdas = [real.lambda_avg for real in self.realizations]
        self.avg_lambda = stat_module.mean(lambdas)
        self.std_lambda = stat_module.stdev(lambdas) if len(lambdas) > 1 else 0.0

        mus = [real.mu_avg for real in self.realizations]
        self.avg_mu = stat_module.mean(mus)
        self.std_mu = stat_module.stdev(mus) if len(mus) > 1 else 0.0

        # Вероятность отказа
        p_rejections = [real.p_rejection for real in self.realizations]
        self.avg_p_rejection = stat_module.mean(p_rejections)
        self.std_p_rejection = stat_module.stdev(p_rejections) if len(p_rejections) > 1 else 0.0

        # Пропускная способность
        throughputs = [real.absolute_throughput for real in self.realizations]
        self.avg_absolute_throughput = stat_module.mean(throughputs)
        self.std_absolute_throughput = stat_module.stdev(throughputs) if len(throughputs) > 1 else 0.0

        # Длина очереди
        queue_lengths = [real.avg_queue_length for real in self.realizations]
        self.avg_queue_length = stat_module.mean(queue_lengths)
        self.std_queue_length = stat_module.stdev(queue_lengths) if len(queue_lengths) > 1 else 0.0

        # Время ожидания
        wait_times = [real.avg_wait_time for real in self.realizations]
        self.avg_wait_time = stat_module.mean(wait_times)
        self.std_wait_time = stat_module.stdev(wait_times) if len(wait_times) > 1 else 0.0

        # Время в системе
        system_times = [real.avg_system_time for real in self.realizations]
        self.avg_system_time = stat_module.mean(system_times)
        self.std_system_time = stat_module.stdev(system_times) if len(system_times) > 1 else 0.0

        # Число занятых каналов
        busy_channels = [real.avg_busy_channels for real in self.realizations]
        self.avg_busy_channels = stat_module.mean(busy_channels)
        self.std_busy_channels = stat_module.stdev(busy_channels) if len(busy_channels) > 1 else 0.0

    def get_characteristic(self, name: str) -> tuple:
        """
        Получить значение характеристики (среднее, стд.откл.).

        Args:
            name: Имя характеристики (например, 'queue_length', 'wait_time')

        Returns:
            Кортеж (среднее, стандартное отклонение)
        """
        mapping = {
            'lambda': (self.avg_lambda, self.std_lambda),
            'mu': (self.avg_mu, self.std_mu),
            'p_rejection': (self.avg_p_rejection, self.std_p_rejection),
            'absolute_throughput': (self.avg_absolute_throughput, self.std_absolute_throughput),
            'queue_length': (self.avg_queue_length, self.std_queue_length),
            'wait_time': (self.avg_wait_time, self.std_wait_time),
            'system_time': (self.avg_system_time, self.std_system_time),
            'busy_channels': (self.avg_busy_channels, self.std_busy_channels),
        }
        return mapping.get(name, (0.0, 0.0))

    def to_dict(self) -> Dict:
        """Преобразовать в словарь для сохранения/вывода."""
        return {
            'N_realizations': self.N_realizations,
            'avg_probabilities': self.avg_probabilities,
            'std_probabilities': self.std_probabilities,
            'avg_lambda': self.avg_lambda,
            'std_lambda': self.std_lambda,
            'avg_mu': self.avg_mu,
            'std_mu': self.std_mu,
            'avg_p_rejection': self.avg_p_rejection,
            'std_p_rejection': self.std_p_rejection,
            'avg_absolute_throughput': self.avg_absolute_throughput,
            'std_absolute_throughput': self.std_absolute_throughput,
            'avg_queue_length': self.avg_queue_length,
            'std_queue_length': self.std_queue_length,
            'avg_wait_time': self.avg_wait_time,
            'std_wait_time': self.std_wait_time,
            'avg_system_time': self.avg_system_time,
            'std_system_time': self.std_system_time,
            'avg_busy_channels': self.avg_busy_channels,
            'std_busy_channels': self.std_busy_channels,
        }


# ============================================================================
# ТЕСТИРОВАНИЕ
# ============================================================================

if __name__ == '__main__':
    from simulation_engine import SimulationEngine
    from config import DistributionType

    print("=" * 70)
    print("ТЕСТИРОВАНИЕ СТАТИСТИКИ (Монте-Карло)")
    print("=" * 70)

    print("\nЗапуск 10 реализаций M/M/1 (λ=0.4, μ=0.5, T=5000)")
    print("-" * 70)

    # Создать симулятор
    engine = SimulationEngine(
        n_channels=1,
        m_queue=None,
        lambda_param=0.4,
        mu_param=0.5,
        arrival_dist=DistributionType.EXPONENTIAL,
        service_dist=DistributionType.EXPONENTIAL,
        seed=18
    )

    # Запустить 10 реализаций
    realizations = []
    for i in range(10):
        result = engine.run_single_realization(T=5000)
        real_stats = RealizationStatistics.from_simulation_result(result)
        realizations.append(real_stats)
        print(f"  Реализация {i+1}: λ̄={real_stats.lambda_avg:.4f}, "
              f"r̄={real_stats.avg_queue_length:.4f}, "
              f"t̄_ож={real_stats.avg_wait_time:.4f}")

    # Агрегировать результаты
    multi_stats = MultiRealizationStatistics(N_realizations=10, realizations=realizations)
    multi_stats.compute_statistics()

    print(f"\nАгрегированные результаты ({multi_stats.N_realizations} реализаций):")
    print(f"  λ̄ = {multi_stats.avg_lambda:.6f} ± {multi_stats.std_lambda:.6f}")
    print(f"  μ̄ = {multi_stats.avg_mu:.6f} ± {multi_stats.std_mu:.6f}")
    print(f"  r̄ = {multi_stats.avg_queue_length:.4f} ± {multi_stats.std_queue_length:.4f}")
    print(f"  t̄_ож = {multi_stats.avg_wait_time:.4f} ± {multi_stats.std_wait_time:.4f} мин")
    print(f"  t̄_сист = {multi_stats.avg_system_time:.4f} ± {multi_stats.std_system_time:.4f} мин")
    print(f"  A = {multi_stats.avg_absolute_throughput:.6f} ± {multi_stats.std_absolute_throughput:.6f}")

    print(f"\nВероятности состояний (первые 5):")
    for state in sorted(multi_stats.avg_probabilities.keys())[:5]:
        avg = multi_stats.avg_probabilities[state]
        std = multi_stats.std_probabilities[state]
        print(f"  p_{state} = {avg:.6f} ± {std:.6f}")

    print("\n" + "=" * 70)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 70)
