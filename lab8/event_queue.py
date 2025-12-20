# -*- coding: utf-8 -*-
"""
Управление событиями в дискретно-событийной симуляции.

Использует приоритетную очередь (heapq) для упорядочивания событий по времени.
"""

import heapq
from dataclasses import dataclass, field
from typing import Optional
from config import EventType


@dataclass(order=True)
class Event:
    """
    Представляет событие в дискретно-событийной симуляции.

    Атрибуты:
        time: Время наступления события (для упорядочивания)
        event_type: Тип события (ARRIVAL или END_SERVICE)
        request_id: ID заявки, связанной с событием
        channel_id: ID канала (для END_SERVICE), None для ARRIVAL
    """
    time: float
    event_type: EventType = field(compare=False)
    request_id: int = field(compare=False)
    channel_id: Optional[int] = field(default=None, compare=False)

    def __repr__(self):
        if self.event_type == EventType.ARRIVAL:
            return f"Event(time={self.time:.4f}, ARRIVAL, req_id={self.request_id})"
        else:
            return (f"Event(time={self.time:.4f}, END_SERVICE, "
                    f"req_id={self.request_id}, ch_id={self.channel_id})")


class EventQueue:
    """
    Приоритетная очередь событий для управления ходом симуляции.

    События упорядочиваются по времени наступления. Событие с наименьшим
    временем извлекается первым.

    Использует встроенный модуль heapq для эффективной реализации.
    """

    def __init__(self):
        """Инициализация пустой очереди событий."""
        self._heap = []
        self._event_count = 0  # Для отслеживания ID событий

    def push(self, event: Event) -> None:
        """
        Добавить событие в очередь.

        Args:
            event: Событие для добавления
        """
        heapq.heappush(self._heap, event)

    def pop(self) -> Event:
        """
        Извлечь событие с наименьшим временем из очереди.

        Returns:
            Событие с наименьшим временем

        Raises:
            IndexError: Если очередь пуста
        """
        if not self._heap:
            raise IndexError("Очередь событий пуста")
        return heapq.heappop(self._heap)

    def peek(self) -> Event:
        """
        Просмотреть событие с наименьшим временем без извлечения.

        Returns:
            Событие с наименьшим временем

        Raises:
            IndexError: Если очередь пуста
        """
        if not self._heap:
            raise IndexError("Очередь событий пуста")
        return self._heap[0]

    def is_empty(self) -> bool:
        """
        Проверить, пуста ли очередь.

        Returns:
            True если очередь пуста, False в противном случае
        """
        return len(self._heap) == 0

    def size(self) -> int:
        """
        Получить количество событий в очереди.

        Returns:
            Число событий в очереди
        """
        return len(self._heap)

    def clear(self) -> None:
        """Очистить очередь от всех событий."""
        self._heap.clear()

    def __len__(self):
        """Возвращает количество событий (для len())."""
        return len(self._heap)

    def __bool__(self):
        """Проверка на пустоту (для if queue: ...  )."""
        return len(self._heap) > 0

    def __repr__(self):
        """Строковое представление очереди."""
        return f"EventQueue(size={len(self._heap)})"

    def debug_print(self):
        """Вывести все события в очереди (для отладки)."""
        print(f"EventQueue имеет {len(self._heap)} событий:")
        for i, event in enumerate(sorted(self._heap, key=lambda e: e.time)):
            print(f"  [{i}] {event}")


# ============================================================================
# ТЕСТИРОВАНИЕ
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("ТЕСТИРОВАНИЕ ОЧЕРЕДИ СОБЫТИЙ")
    print("=" * 70)

    # Создание очереди
    queue = EventQueue()
    print(f"\n1. Создана пустая очередь: {queue}")
    print(f"   Размер: {queue.size()}, Пуста: {queue.is_empty()}")

    # Добавление событий в неупорядоченном порядке
    print("\n2. Добавление событий в неупорядоченном порядке:")
    events_to_add = [
        Event(time=5.0, event_type=EventType.ARRIVAL, request_id=1),
        Event(time=1.0, event_type=EventType.ARRIVAL, request_id=2),
        Event(time=3.5, event_type=EventType.END_SERVICE, request_id=1, channel_id=0),
        Event(time=2.0, event_type=EventType.ARRIVAL, request_id=3),
        Event(time=8.0, event_type=EventType.END_SERVICE, request_id=2, channel_id=1),
    ]

    for event in events_to_add:
        queue.push(event)
        print(f"   Добавлено: {event}")

    print(f"\n   Размер очереди: {queue.size()}")

    # Извлечение событий
    print("\n3. Извлечение событий (в порядке увеличения времени):")
    while not queue.is_empty():
        event = queue.pop()
        print(f"   Извлечено: {event}")

    print(f"\n   Очередь пуста: {queue.is_empty()}")

    # Тест с перемешанными временами
    print("\n4. Проверка упорядочивания на большом наборе:")
    queue.clear()
    import random
    random.seed(42)

    times = [random.random() * 100 for _ in range(10)]
    for i, time in enumerate(times):
        queue.push(Event(
            time=time,
            event_type=EventType.ARRIVAL if i % 2 == 0 else EventType.END_SERVICE,
            request_id=i,
            channel_id=0 if i % 2 == 1 else None
        ))

    print(f"   Добавлено {queue.size()} событий с случайными временами")

    sorted_times = []
    while not queue.is_empty():
        event = queue.pop()
        sorted_times.append(event.time)

    is_sorted = all(sorted_times[i] <= sorted_times[i + 1] for i in range(len(sorted_times) - 1))
    print(f"   События упорядочены: {is_sorted}")
    print(f"   Времена: {[f'{t:.2f}' for t in sorted_times]}")

    print("\n" + "=" * 70)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 70)
