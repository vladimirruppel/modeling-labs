# -*- coding: utf-8 -*-
"""
Дискретно-событийный симулятор для систем массового обслуживания.

Реализует основной алгоритм моделирования немарковских СМО методом Монте-Карло.
"""

from dataclasses import dataclass, field
from collections import deque
from typing import Dict, List, Optional, Tuple
from event_queue import Event, EventQueue
from config import EventType, DistributionType
from random_generator import RandomGenerator


@dataclass
class Request:
    """
    Представляет заявку (клиента) в системе.

    Атрибуты:
        request_id: Уникальный ID заявки
        arrival_time: Время прибытия в систему
        service_start_time: Время начала обслуживания (None если ещё не начиналось)
        service_end_time: Время завершения обслуживания (None если ещё идёт)
        queue_entry_time: Время вступления в очередь (None если не было)
        queue_exit_time: Время выхода из очереди (None если не было)
        was_rejected: True если заявка была отклонена
        service_duration: Длительность обслуживания
    """
    request_id: int
    arrival_time: float
    service_duration: float
    service_start_time: Optional[float] = None
    service_end_time: Optional[float] = None
    queue_entry_time: Optional[float] = None
    queue_exit_time: Optional[float] = None
    was_rejected: bool = False

    def get_queue_time(self) -> float:
        """Получить время в очереди (0 если не было)."""
        if self.queue_entry_time is None or self.queue_exit_time is None:
            return 0.0
        return self.queue_exit_time - self.queue_entry_time

    def get_wait_time(self) -> float:
        """Получить время ожидания начала обслуживания (0 если пришёл и сразу обслужили)."""
        if self.service_start_time is None or self.queue_entry_time is None:
            return 0.0
        return self.service_start_time - self.queue_entry_time

    def get_system_time(self) -> float:
        """Получить время в системе (от прибытия до завершения обслуживания)."""
        if self.service_end_time is None:
            return 0.0
        return self.service_end_time - self.arrival_time


@dataclass
class QueueSystem:
    """
    Представляет состояние системы массового обслуживания.

    Атрибуты:
        n_channels: Число каналов обслуживания
        m_queue: Максимум мест в очереди (None = бесконечна)
        channels: Список занятых заявок в каналах (None = свободен)
        queue: Очередь ожидающих заявок (deque)
        current_time: Текущее время в системе
        state_history: История времён в каждом состоянии
    """
    n_channels: int
    m_queue: Optional[int]
    channels: List[Optional[Request]] = field(default_factory=list)
    queue: deque = field(default_factory=deque)
    current_time: float = 0.0
    state_history: Dict[int, float] = field(default_factory=dict)

    def __post_init__(self):
        """Инициализация каналов и истории состояний."""
        self.channels = [None] * self.n_channels
        # Инициализируем историю состояний: для каждого возможного состояния
        for state in range(self.n_channels + (self.m_queue or 0) + 1):
            self.state_history[state] = 0.0

    def get_busy_channels(self) -> int:
        """Получить число занятых каналов."""
        return sum(1 for ch in self.channels if ch is not None)

    def get_queue_length(self) -> int:
        """Получить число заявок в очереди."""
        return len(self.queue)

    def get_state(self) -> int:
        """Получить текущее состояние системы (число занятых + число в очереди)."""
        return self.get_busy_channels() + self.get_queue_length()

    def get_free_channel_id(self) -> Optional[int]:
        """Получить ID свободного канала (None если все заняты)."""
        for i, ch in enumerate(self.channels):
            if ch is None:
                return i
        return None

    def is_queue_full(self) -> bool:
        """Проверить, полна ли очередь."""
        if self.m_queue is None:
            return False
        return len(self.queue) >= self.m_queue

    def start_service(self, channel_id: int, request: Request) -> None:
        """Начать обслуживание заявки в канале."""
        self.channels[channel_id] = request
        request.service_start_time = self.current_time
        request.queue_exit_time = self.current_time

    def finish_service(self, channel_id: int) -> Request:
        """Завершить обслуживание и освободить канал."""
        request = self.channels[channel_id]
        request.service_end_time = self.current_time
        self.channels[channel_id] = None
        return request


class SimulationEngine:
    """
    Главный класс для управления симуляцией СМО.

    Реализует дискретно-событийный алгоритм моделирования.
    """

    def __init__(self, n_channels: int, m_queue: Optional[int] = None,
                 lambda_param: float = 0.4, mu_param: float = 0.5,
                 arrival_dist: DistributionType = DistributionType.EXPONENTIAL,
                 service_dist: DistributionType = DistributionType.EXPONENTIAL,
                 arrival_params: Dict = None, service_params: Dict = None,
                 seed: int = None):
        """
        Инициализация симулятора.

        Args:
            n_channels: Число каналов обслуживания
            m_queue: Максимум мест в очереди (None = бесконечна)
            lambda_param: Интенсивность входящего потока
            mu_param: Интенсивность обслуживания
            arrival_dist: Распределение прибытия
            service_dist: Распределение обслуживания
            arrival_params: Дополнительные параметры для распределения прибытия
            service_params: Дополнительные параметры для распределения обслуживания
            seed: Seed для воспроизводимости
        """
        self.n_channels = n_channels
        self.m_queue = m_queue
        self.lambda_param = lambda_param
        self.mu_param = mu_param
        self.arrival_dist = arrival_dist
        self.service_dist = service_dist
        self.arrival_params = arrival_params or {}
        self.service_params = service_params or {}
        self.seed = seed

        # Инициализация генератора случайных чисел
        self.rng = RandomGenerator(seed=seed)

        # Инициализация системы
        self.system = QueueSystem(n_channels=n_channels, m_queue=m_queue)
        self.event_queue = EventQueue()
        self.request_counter = 0

        # Статистика
        self.all_requests = []
        self.rejected_requests = []

    def _generate_arrival_interval(self) -> float:
        """Генерировать интервал до следующего прибытия."""
        if self.arrival_dist == DistributionType.EXPONENTIAL:
            return self.rng.generate_exponential(self.lambda_param)
        elif self.arrival_dist == DistributionType.WEIBULL:
            return self.rng.generate_weibull(**self.arrival_params)
        elif self.arrival_dist == DistributionType.GAMMA:
            return self.rng.generate_gamma(**self.arrival_params)
        elif self.arrival_dist == DistributionType.NORMAL:
            return max(0.001, self.rng.generate_normal(**self.arrival_params))
        else:
            raise ValueError(f"Неизвестное распределение: {self.arrival_dist}")

    def _generate_service_time(self) -> float:
        """Генерировать время обслуживания."""
        if self.service_dist == DistributionType.EXPONENTIAL:
            return self.rng.generate_exponential(self.mu_param)
        elif self.service_dist == DistributionType.WEIBULL:
            return self.rng.generate_weibull(**self.service_params)
        elif self.service_dist == DistributionType.GAMMA:
            return self.rng.generate_gamma(**self.service_params)
        elif self.service_dist == DistributionType.NORMAL:
            return max(0.001, self.rng.generate_normal(**self.service_params))
        else:
            raise ValueError(f"Неизвестное распределение: {self.service_dist}")

    def _schedule_arrival(self, time: float) -> None:
        """Запланировать следующее прибытие."""
        arrival_interval = self._generate_arrival_interval()
        next_arrival_time = time + arrival_interval
        event = Event(
            time=next_arrival_time,
            event_type=EventType.ARRIVAL,
            request_id=self.request_counter
        )
        self.event_queue.push(event)

    def _schedule_service_end(self, time: float, request_id: int,
                              channel_id: int, service_time: float) -> None:
        """Запланировать завершение обслуживания."""
        end_time = time + service_time
        event = Event(
            time=end_time,
            event_type=EventType.END_SERVICE,
            request_id=request_id,
            channel_id=channel_id
        )
        self.event_queue.push(event)

    def _handle_arrival(self, time: float) -> None:
        """Обработать прибытие новой заявки."""
        self.system.current_time = time

        # Создать новую заявку
        self.request_counter += 1
        service_time = self._generate_service_time()
        request = Request(
            request_id=self.request_counter - 1,
            arrival_time=time,
            service_duration=service_time
        )

        # Проверить наличие свободного канала
        free_channel_id = self.system.get_free_channel_id()

        if free_channel_id is not None:
            # Свободный канал есть - начать обслуживание сразу
            self.system.start_service(free_channel_id, request)
            self._schedule_service_end(time, request.request_id, free_channel_id, service_time)
        elif not self.system.is_queue_full():
            # Очередь не полна - поставить в очередь
            request.queue_entry_time = time
            self.system.queue.append(request)
        else:
            # Очередь полна - отказать
            request.was_rejected = True
            self.rejected_requests.append(request)

        self.all_requests.append(request)

        # Запланировать следующее прибытие
        self._schedule_arrival(time)

    def _handle_service_end(self, time: float, request_id: int, channel_id: int) -> None:
        """Обработать завершение обслуживания."""
        self.system.current_time = time

        # Завершить обслуживание текущей заявки
        finished_request = self.system.finish_service(channel_id)

        # Проверить, есть ли заявки в очереди
        if self.system.queue:
            # Начать обслуживание следующей из очереди
            next_request = self.system.queue.popleft()
            next_request.queue_exit_time = time
            service_time = next_request.service_duration
            self.system.start_service(channel_id, next_request)
            self._schedule_service_end(time, next_request.request_id, channel_id, service_time)

    def run_single_realization(self, T: float) -> Dict:
        """
        Запустить одну реализацию симуляции.

        Args:
            T: Интервал моделирования (в минутах)

        Returns:
            Словарь с результатами и статистикой реализации
        """
        # Инициализация
        self.system = QueueSystem(n_channels=self.n_channels, m_queue=self.m_queue)
        self.event_queue = EventQueue()
        self.request_counter = 0
        self.all_requests = []
        self.rejected_requests = []

        # Запланировать первое прибытие
        self._schedule_arrival(0.0)

        # Основной цикл симуляции
        last_state_time = 0.0
        last_state = 0

        while not self.event_queue.is_empty():
            event = self.event_queue.pop()

            # Если событие за пределами интервала T, остановить
            if event.time > T:
                break

            # Записать время в предыдущем состоянии
            state_duration = event.time - last_state_time
            if last_state not in self.system.state_history:
                self.system.state_history[last_state] = 0.0
            self.system.state_history[last_state] += state_duration

            # Обработать событие
            if event.event_type == EventType.ARRIVAL:
                self._handle_arrival(event.time)
            elif event.event_type == EventType.END_SERVICE:
                self._handle_service_end(event.time, event.request_id, event.channel_id)

            # Обновить последнее состояние
            last_state = self.system.get_state()
            last_state_time = event.time

        # Добавить оставшееся время до конца интервала
        remaining_time = T - last_state_time
        if remaining_time > 0:
            if last_state not in self.system.state_history:
                self.system.state_history[last_state] = 0.0
            self.system.state_history[last_state] += remaining_time

        # Вычислить статистику
        return self._calculate_statistics(T)

    def _calculate_statistics(self, T: float) -> Dict:
        """Вычислить статистику на основе результатов симуляции."""
        # Вероятности состояний
        probabilities = {}
        for state, duration in self.system.state_history.items():
            probabilities[state] = duration / T

        # Интенсивности
        N = len(self.all_requests)  # всего прибыло заявок
        N_served = len([r for r in self.all_requests if not r.was_rejected])
        N_rejected = len(self.rejected_requests)

        lambda_avg = N / T if T > 0 else 0.0

        # Среднее время обслуживания
        service_times = [r.service_duration for r in self.all_requests if r.service_start_time is not None]
        t_ob_avg = sum(service_times) / len(service_times) if service_times else 0.0
        mu_avg = (1.0 / t_ob_avg) if t_ob_avg > 0 else 0.0

        # Вероятность отказа и пропускная способность
        p_rejection = N_rejected / N if N > 0 else 0.0
        relative_throughput = 1.0 - p_rejection
        absolute_throughput = lambda_avg * relative_throughput

        # Среднее число занятых каналов
        avg_busy = sum(i * probabilities.get(i, 0) for i in range(self.n_channels + 1))

        # Средняя длина очереди
        avg_queue = sum((i - self.n_channels) * probabilities.get(i, 0)
                       for i in range(self.n_channels + 1, len(probabilities)))

        # Времена ожидания
        wait_times = [r.get_wait_time() for r in self.all_requests if not r.was_rejected and r.get_wait_time() > 0]
        avg_wait_time = sum(wait_times) / len(wait_times) if wait_times else 0.0

        # Время в системе
        system_times = [r.get_system_time() for r in self.all_requests if not r.was_rejected]
        avg_system_time = sum(system_times) / len(system_times) if system_times else 0.0

        return {
            'T': T,
            'N_arrivals': N,
            'N_served': N_served,
            'N_rejected': N_rejected,
            'probabilities': probabilities,
            'lambda_avg': lambda_avg,
            'mu_avg': mu_avg,
            'p_rejection': p_rejection,
            'relative_throughput': relative_throughput,
            'absolute_throughput': absolute_throughput,
            'avg_busy_channels': avg_busy,
            'avg_queue_length': avg_queue,
            'avg_wait_time': avg_wait_time,
            'avg_system_time': avg_system_time,
            'service_times': service_times,
            'wait_times': wait_times,
            'system_times': system_times
        }


if __name__ == '__main__':
    print("=" * 70)
    print("ТЕСТИРОВАНИЕ СИМУЛЯТОРА")
    print("=" * 70)

    # Тест 1: M/M/1 с экспоненциальным распределением
    print("\n1. Симуляция M/M/1 (λ=0.4, μ=0.5, T=10000)")
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

    results = engine.run_single_realization(T=10000)

    print(f"Прибыло заявок: {results['N_arrivals']}")
    print(f"Обслужено: {results['N_served']}")
    print(f"Отказано: {results['N_rejected']}")
    print(f"\nХарактеристики:")
    print(f"  λ̄ = {results['lambda_avg']:.6f}")
    print(f"  μ̄ = {results['mu_avg']:.6f}")
    print(f"  p_отказ = {results['p_rejection']:.6f}")
    print(f"  Пропускная способность A = {results['absolute_throughput']:.6f}")
    print(f"  Средняя длина очереди r̄ = {results['avg_queue_length']:.4f}")
    print(f"  Среднее время ожидания t̄_ож = {results['avg_wait_time']:.4f} мин")
    print(f"  Среднее время в системе t̄_сист = {results['avg_system_time']:.4f} мин")

    # Вероятности состояний
    print(f"\nВероятности состояний:")
    for state in sorted(results['probabilities'].keys())[:10]:
        print(f"  p_{state} = {results['probabilities'][state]:.6f}")

    print("\n" + "=" * 70)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 70)
