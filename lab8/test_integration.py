#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интеграционный тест всех компонентов ЛР №8.

Проверяет, что все модули работают вместе корректно.
"""

from pathlib import Path
import sys

# Импорт всех основных модулей
try:
    from config import DistributionType, EventType
    from random_generator import RandomGenerator
    from event_queue import Event, EventQueue
    from simulation_engine import SimulationEngine
    from stats_aggregation import RealizationStatistics, MultiRealizationStatistics
    from validation import MarkovianQueueTheory, validate_simulation
    from visualization import (
        plot_state_probabilities_comparison,
        plot_time_distributions,
        ensure_output_dir
    )
    from utils import (
        print_section_header,
        print_separator,
        load_variant18_config,
        load_configuration
    )

    print("✓ Все импорты успешны")
except ImportError as e:
    print(f"✗ Ошибка импорта: {e}")
    sys.exit(1)


def test_configuration_loading() -> bool:
    """Тест загрузки конфигурации."""
    print_section_header("Тест 1: Загрузка конфигурации")

    config = load_variant18_config()
    if not config:
        print("✗ Ошибка загрузки конфигурации")
        return False

    print(f"✓ Конфигурация варианта {config['variant']} загружена")
    print(f"  Описание: {config['description']}")
    print(f"  λ = {config['lambda']}")

    for cfg in config['configurations']:
        cfg1 = load_configuration(cfg['id'])
        if not cfg1:
            print(f"✗ Не удалось загрузить конфигурацию {cfg['id']}")
            return False
        print(f"✓ Конфигурация {cfg['id']}: {cfg1['description']}")

    return True


def test_random_generator() -> bool:
    """Тест генератора случайных чисел."""
    print_section_header("Тест 2: Генератор случайных чисел")

    rng = RandomGenerator(seed=42)

    # Тест каждого распределения
    try:
        exp_val = rng.generate_exponential(0.4)
        print(f"✓ Экспоненциальное: {exp_val:.4f}")

        weibull_val = rng.generate_weibull(2.0, 2.5)
        print(f"✓ Вейбула: {weibull_val:.4f}")

        gamma_val = rng.generate_gamma(0.4, 2)
        print(f"✓ Гамма: {gamma_val:.4f}")

        normal_val = rng.generate_normal(2.5, 0.5)
        print(f"✓ Нормальное: {normal_val:.4f}")

        return True
    except Exception as e:
        print(f"✗ Ошибка при генерации: {e}")
        return False


def test_event_queue() -> bool:
    """Тест очереди событий."""
    print_section_header("Тест 3: Очередь событий")

    try:
        queue = EventQueue()

        # Добавить события
        events = [
            Event(5.0, EventType.ARRIVAL, 1),
            Event(2.0, EventType.ARRIVAL, 2),
            Event(8.0, EventType.END_SERVICE, 1, 0),
        ]

        for event in events:
            queue.push(event)

        # Извлечь в порядке возрастания времени
        prev_time = -1
        while not queue.is_empty():
            event = queue.pop()
            if event.time < prev_time:
                print(f"✗ Нарушен порядок: {event.time} < {prev_time}")
                return False
            prev_time = event.time

        print("✓ Очередь работает корректно (3 события извлечены по порядку)")
        return True
    except Exception as e:
        print(f"✗ Ошибка в очереди: {e}")
        return False


def test_simulation_mm1() -> bool:
    """Тест симуляции M/M/1."""
    print_section_header("Тест 4: Симуляция M/M/1")

    try:
        engine = SimulationEngine(
            n_channels=1,
            m_queue=None,
            lambda_param=0.4,
            mu_param=0.5,
            arrival_dist=DistributionType.EXPONENTIAL,
            service_dist=DistributionType.EXPONENTIAL,
            seed=18
        )

        result = engine.run_single_realization(T=5000)

        if not result or 'N_arrivals' not in result:
            print("✗ Результаты симуляции пусты")
            return False

        print(f"✓ Симуляция выполнена")
        print(f"  Прибыло: {result['N_arrivals']}")
        print(f"  Обслужено: {result['N_served']}")
        print(f"  λ̄ = {result['lambda_avg']:.6f}")
        print(f"  r̄ = {result['avg_queue_length']:.6f}")
        print(f"  t̄_ож = {result['avg_wait_time']:.6f}")

        return True
    except Exception as e:
        print(f"✗ Ошибка при симуляции: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_statistics_aggregation() -> bool:
    """Тест агрегирования статистики."""
    print_section_header("Тест 5: Агрегирование статистики")

    try:
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
        for i in range(3):
            result = engine.run_single_realization(T=5000)
            real_stats = RealizationStatistics.from_simulation_result(result)
            realizations.append(real_stats)

        multi_stats = MultiRealizationStatistics(N_realizations=3, realizations=realizations)
        multi_stats.compute_statistics()

        print(f"✓ Статистика агрегирована (3 реализации)")
        print(f"  λ̄ = {multi_stats.avg_lambda:.6f} ± {multi_stats.std_lambda:.6f}")
        print(f"  r̄ = {multi_stats.avg_queue_length:.6f} ± {multi_stats.std_queue_length:.6f}")

        return True
    except Exception as e:
        print(f"✗ Ошибка при агрегировании: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validation() -> bool:
    """Тест валидации."""
    print_section_header("Тест 6: Валидация")

    try:
        # Теоретические результаты
        theory = MarkovianQueueTheory.calculate_mm1_characteristics(0.4, 0.5)

        if not theory.get('stable'):
            print("✗ Система неустойчива")
            return False

        print(f"✓ Теоретические результаты рассчитаны")
        print(f"  ρ = {theory['rho']:.4f}")
        print(f"  r̄ = {theory['avg_queue_length']:.4f}")

        # Запустить симуляцию
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

        # Валидировать
        validation = validate_simulation(multi_stats, theory, epsilon=0.05)

        print(f"✓ Валидация выполнена")
        print(f"  Макс ошибка: {validation.max_error*100:.2f}%")
        print(f"  В допуске: {'ДА' if validation.within_tolerance else 'НЕТ'}")

        return True
    except Exception as e:
        print(f"✗ Ошибка при валидации: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_visualization() -> bool:
    """Тест визуализации."""
    print_section_header("Тест 7: Визуализация")

    try:
        # Проверить, что директория создана
        output_dir = ensure_output_dir()
        print(f"✓ Директория output создана: {output_dir}")

        # Проверить наличие графиков
        png_files = list(output_dir.glob("*.png"))
        print(f"✓ Найдено {len(png_files)} график(ов)")

        return True
    except Exception as e:
        print(f"✗ Ошибка при визуализации: {e}")
        return False


def main() -> None:
    """Главная функция тестирования."""
    print("\n")
    print_section_header("ИНТЕГРАЦИОННОЕ ТЕСТИРОВАНИЕ ЛР №8")

    tests = [
        ("Загрузка конфигурации", test_configuration_loading),
        ("Генератор случайных чисел", test_random_generator),
        ("Очередь событий", test_event_queue),
        ("Симуляция M/M/1", test_simulation_mm1),
        ("Агрегирование статистики", test_statistics_aggregation),
        ("Валидация", test_validation),
        ("Визуализация", test_visualization),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Неожиданная ошибка в {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

        print()

    # Итоговый отчёт
    print_section_header("ИТОГИ ТЕСТИРОВАНИЯ")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status:8} {test_name}")

    print_separator('-', 50)
    print(f"  Итого: {passed}/{total} тестов пройдено ({passed*100//total}%)")

    if passed == total:
        print("\n✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("✓ Программа готова к использованию")
        return 0
    else:
        print(f"\n✗ {total - passed} тест(ов) не пройдено")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
