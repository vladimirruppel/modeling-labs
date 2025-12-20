#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЛР 7: Определение характеристик марковских систем массового обслуживания (СМО)

Программа позволяет анализировать различные типы марковских СМО:
- M|M|n|0 - с отказами
- M|M|1|m - одноканальные с конечной очередью
- M|M|1|∞ - одноканальные с бесконечной очередью
- M|M|n|m - многоканальные с конечной очередью
- M|M|n|∞ - многоканальные с бесконечной очередью
- Замкнутые СМО (одно- и многоканальные)
- Полный анализ Варианта 18: Предприятие быстрого питания
"""

from colorama import Fore, Style, init
import sys

from utils import (
    print_section_header, print_separator, print_results_table,
    print_probabilities_table, input_intensity_or_time, ask_continue,
    print_stability_warning, ask_choice, format_value
)
from smo_systems import (
    MMn0, MM1m, MM1inf, MMnm, MMninf,
    ClosedSingle, ClosedMulti
)
from calculations import calculate_economic_costs

# Инициализация colorama
init(autoreset=True)


def print_main_menu():
    """Выводит главное меню программы"""
    print_section_header("ЛР 7: Марковские СМО")
    print(f"\n{Fore.GREEN}Выберите тип СМО для анализа:{Style.RESET_ALL}\n")
    print("  1. M|M|n|0   - Многоканальная с отказами")
    print("  2. M|M|1|m   - Одноканальная с конечной очередью")
    print("  3. M|M|1|∞   - Одноканальная с бесконечной очередью")
    print("  4. M|M|n|m   - Многоканальная с конечной очередью")
    print("  5. M|M|n|∞   - Многоканальная с бесконечной очередью")
    print("  6. Замкнутая - Одноканальная")
    print("  7. Замкнутая - Многоканальная")
    print("  8. Вариант 18 - Полный анализ (предприятие быстрого питания)")
    print("  9. Выход")
    print()


def input_lambda_mu():
    """Получает ввод λ и μ от пользователя"""
    print(f"\n{Fore.CYAN}Ввод параметров потоков:{Style.RESET_ALL}")

    lambda_val = input_intensity_or_time("Входящий поток (λ)")
    print()
    mu_val = input_intensity_or_time("Обслуживание (μ)")

    return lambda_val, mu_val


def handle_mmn0():
    """Обработка типа M|M|n|0"""
    while True:
        print_section_header("M|M|n|0 - Многоканальная с отказами")

        try:
            lambda_val, mu_val = input_lambda_mu()

            n = int(input(f"\n{Fore.GREEN}Введите количество каналов (n): {Style.RESET_ALL}"))
            if n < 1:
                print(f"{Fore.RED}Ошибка: n должно быть >= 1{Style.RESET_ALL}")
                continue

            # Создание системы
            system = MMn0(n_channels=n, lambda_val=lambda_val, mu_val=mu_val)
            print_stability_warning(lambda_val, mu_val, n)

            # Вычисление характеристик
            results = system.calculate_all_characteristics()

            # Вывод результатов
            print_section_header("Результаты расчета")

            # Основные параметры
            params = {
                'Входящий поток λ': format_value(results['lambda']),
                'Обслуживание μ': format_value(results['mu']),
                'Параметр ρ = λ/μ': format_value(results['rho']),
                'Количество каналов': results['n_channels']
            }
            print_results_table(params, "Входные параметры")

            # Вероятности состояний
            print_probabilities_table(results['probabilities'])

            # Характеристики производительности
            perf = {
                'Вероятность отказа (P_отк)': format_value(results['p_rejection']),
                'Относительная пропускная способность (q)': format_value(results['relative_throughput']),
                'Абсолютная пропускная способность (A)': format_value(results['absolute_throughput']),
                'Среднее количество занятых каналов': format_value(results['avg_busy_channels'])
            }
            print_results_table(perf, "Характеристики производительности")

        except ValueError as e:
            print(f"{Fore.RED}Ошибка: {e}{Style.RESET_ALL}")
            continue
        except Exception as e:
            print(f"{Fore.RED}Ошибка при расчете: {e}{Style.RESET_ALL}")
            continue

        if not ask_continue():
            break


def handle_mm1m():
    """Обработка типа M|M|1|m"""
    while True:
        print_section_header("M|M|1|m - Одноканальная с конечной очередью")

        try:
            lambda_val, mu_val = input_lambda_mu()

            m = int(input(f"\n{Fore.GREEN}Введите максимум мест в очереди (m): {Style.RESET_ALL}"))
            if m < 0:
                print(f"{Fore.RED}Ошибка: m должно быть >= 0{Style.RESET_ALL}")
                continue

            # Создание системы
            system = MM1m(m_queue=m, lambda_val=lambda_val, mu_val=mu_val)
            print_stability_warning(lambda_val, mu_val, 1)

            # Вычисление характеристик
            results = system.calculate_all_characteristics()

            # Вывод результатов
            print_section_header("Результаты расчета")

            # Основные параметры
            params = {
                'Входящий поток λ': format_value(results['lambda']),
                'Обслуживание μ': format_value(results['mu']),
                'Параметр ρ = λ/μ': format_value(results['rho']),
                'Максимум в очереди (m)': results['m_queue']
            }
            print_results_table(params, "Входные параметры")

            # Вероятности состояний (первые 10)
            prob_display = {k: v for k, v in list(results['probabilities'].items())[:10]}
            print_probabilities_table(prob_display)

            # Характеристики производительности
            perf = {
                'Вероятность отказа (P_отк)': format_value(results['p_rejection']),
                'Относительная пропускная способность (q)': format_value(results['relative_throughput']),
                'Абсолютная пропускная способность (A)': format_value(results['absolute_throughput']),
                'Средняя длина очереди': format_value(results['avg_queue_length']),
                'Среднее время ожидания (мин)': format_value(results['avg_wait_time']),
                'Среднее время в системе (мин)': format_value(results['avg_system_time'])
            }
            print_results_table(perf, "Характеристики производительности")

        except ValueError as e:
            print(f"{Fore.RED}Ошибка: {e}{Style.RESET_ALL}")
            continue
        except Exception as e:
            print(f"{Fore.RED}Ошибка при расчете: {e}{Style.RESET_ALL}")
            continue

        if not ask_continue():
            break


def handle_mm1inf():
    """Обработка типа M|M|1|∞"""
    while True:
        print_section_header("M|M|1|∞ - Одноканальная с бесконечной очередью")

        try:
            lambda_val, mu_val = input_lambda_mu()

            # Создание системы
            system = MM1inf(lambda_val=lambda_val, mu_val=mu_val)
            print_stability_warning(lambda_val, mu_val, 1)

            # Вычисление характеристик
            results = system.calculate_all_characteristics()

            # Вывод результатов
            print_section_header("Результаты расчета")

            # Основные параметры
            params = {
                'Входящий поток λ': format_value(results['lambda']),
                'Обслуживание μ': format_value(results['mu']),
                'Параметр ρ = λ/μ': format_value(results['rho'])
            }
            print_results_table(params, "Входные параметры")

            # Вероятности состояний (первые 15)
            prob_display = {k: v for k, v in list(results['probabilities'].items())[:15]}
            print_probabilities_table(prob_display)

            # Характеристики производительности
            perf = {
                'Вероятность отказа (P_отк)': format_value(results['p_rejection']),
                'Относительная пропускная способность (q)': format_value(results['relative_throughput']),
                'Абсолютная пропускная способность (A)': format_value(results['absolute_throughput']),
                'Средняя длина очереди': format_value(results['avg_queue_length']),
                'Среднее число заявок в системе': format_value(results['avg_system_length']),
                'Среднее время ожидания (мин)': format_value(results['avg_wait_time']),
                'Среднее время в системе (мин)': format_value(results['avg_system_time'])
            }
            print_results_table(perf, "Характеристики производительности")

        except ValueError as e:
            print(f"{Fore.RED}Ошибка: {e}{Style.RESET_ALL}")
            continue
        except Exception as e:
            print(f"{Fore.RED}Ошибка при расчете: {e}{Style.RESET_ALL}")
            continue

        if not ask_continue():
            break


def handle_mmnm():
    """Обработка типа M|M|n|m"""
    while True:
        print_section_header("M|M|n|m - Многоканальная с конечной очередью")

        try:
            lambda_val, mu_val = input_lambda_mu()

            n = int(input(f"\n{Fore.GREEN}Введите количество каналов (n): {Style.RESET_ALL}"))
            if n < 1:
                print(f"{Fore.RED}Ошибка: n должно быть >= 1{Style.RESET_ALL}")
                continue

            m = int(input(f"{Fore.GREEN}Введите максимум мест в очереди (m): {Style.RESET_ALL}"))
            if m < 0:
                print(f"{Fore.RED}Ошибка: m должно быть >= 0{Style.RESET_ALL}")
                continue

            # Создание системы
            system = MMnm(n_channels=n, m_queue=m, lambda_val=lambda_val, mu_val=mu_val)
            print_stability_warning(lambda_val, mu_val, n)

            # Вычисление характеристик
            results = system.calculate_all_characteristics()

            # Вывод результатов
            print_section_header("Результаты расчета")

            # Основные параметры
            params = {
                'Входящий поток λ': format_value(results['lambda']),
                'Обслуживание μ': format_value(results['mu']),
                'Параметр ρ = λ/μ': format_value(results['rho']),
                'Количество каналов': results['n_channels'],
                'Максимум в очереди': results['m_queue']
            }
            print_results_table(params, "Входные параметры")

            # Вероятности состояний
            prob_display = {k: v for k, v in list(results['probabilities'].items())[:15]}
            print_probabilities_table(prob_display)

            # Характеристики производительности
            perf = {
                'Вероятность отказа (P_отк)': format_value(results['p_rejection']),
                'Относительная пропускная способность (q)': format_value(results['relative_throughput']),
                'Абсолютная пропускная способность (A)': format_value(results['absolute_throughput']),
                'Средняя длина очереди': format_value(results['avg_queue_length']),
                'Среднее время ожидания (мин)': format_value(results['avg_wait_time'])
            }
            print_results_table(perf, "Характеристики производительности")

        except ValueError as e:
            print(f"{Fore.RED}Ошибка: {e}{Style.RESET_ALL}")
            continue
        except Exception as e:
            print(f"{Fore.RED}Ошибка при расчете: {e}{Style.RESET_ALL}")
            continue

        if not ask_continue():
            break


def handle_mmninf():
    """Обработка типа M|M|n|∞"""
    while True:
        print_section_header("M|M|n|∞ - Многоканальная с бесконечной очередью")

        try:
            lambda_val, mu_val = input_lambda_mu()

            n = int(input(f"\n{Fore.GREEN}Введите количество каналов (n): {Style.RESET_ALL}"))
            if n < 1:
                print(f"{Fore.RED}Ошибка: n должно быть >= 1{Style.RESET_ALL}")
                continue

            # Создание системы
            system = MMninf(n_channels=n, lambda_val=lambda_val, mu_val=mu_val)
            print_stability_warning(lambda_val, mu_val, n)

            # Вычисление характеристик
            results = system.calculate_all_characteristics()

            # Вывод результатов
            print_section_header("Результаты расчета")

            # Основные параметры
            params = {
                'Входящий поток λ': format_value(results['lambda']),
                'Обслуживание μ': format_value(results['mu']),
                'Параметр ρ = λ/μ': format_value(results['rho']),
                'Количество каналов': results['n_channels'],
                'Условие ρ/n': format_value(results['rho'] / results['n_channels'])
            }
            print_results_table(params, "Входные параметры")

            # Вероятности состояний (первые 15)
            prob_display = {k: v for k, v in list(results['probabilities'].items())[:15]}
            print_probabilities_table(prob_display)

            # Характеристики производительности
            perf = {
                'Абсолютная пропускная способность (A)': format_value(results['absolute_throughput']),
                'Средняя длина очереди': format_value(results['avg_queue_length']),
                'Среднее число заявок в системе': format_value(results['avg_system_length']),
                'Среднее время ожидания (мин)': format_value(results['avg_wait_time']),
                'Среднее время в системе (мин)': format_value(results['avg_system_time'])
            }
            print_results_table(perf, "Характеристики производительности")

        except ValueError as e:
            print(f"{Fore.RED}Ошибка: {e}{Style.RESET_ALL}")
            continue
        except Exception as e:
            print(f"{Fore.RED}Ошибка при расчете: {e}{Style.RESET_ALL}")
            continue

        if not ask_continue():
            break


def handle_closed_single():
    """Обработка замкнутой одноканальной СМО"""
    while True:
        print_section_header("Замкнутая одноканальная СМО")

        try:
            lambda_val, mu_val = input_lambda_mu()

            N = int(input(f"\n{Fore.GREEN}Введите количество источников (N): {Style.RESET_ALL}"))
            if N < 1:
                print(f"{Fore.RED}Ошибка: N должно быть >= 1{Style.RESET_ALL}")
                continue

            # Создание системы
            system = ClosedSingle(N_sources=N, lambda_val=lambda_val, mu_val=mu_val)

            # Вычисление характеристик
            results = system.calculate_all_characteristics()

            # Вывод результатов
            print_section_header("Результаты расчета")

            # Основные параметры
            params = {
                'Интенсивность источника λ': format_value(results['lambda']),
                'Интенсивность обслуживания μ': format_value(results['mu']),
                'Количество источников N': results['N_sources']
            }
            print_results_table(params, "Входные параметры")

            # Вероятности состояний
            print_probabilities_table(results['probabilities'])

            # Характеристики производительности
            perf = {
                'Среднее число заявок в системе': format_value(results['avg_system_length']),
                'Средняя длина очереди': format_value(results['avg_queue_length']),
                'Эффективная интенсивность потока': format_value(results['effective_lambda']),
                'Среднее время ожидания (мин)': format_value(results['avg_wait_time']),
                'Среднее время в системе (мин)': format_value(results['avg_system_time'])
            }
            print_results_table(perf, "Характеристики производительности")

        except ValueError as e:
            print(f"{Fore.RED}Ошибка: {e}{Style.RESET_ALL}")
            continue
        except Exception as e:
            print(f"{Fore.RED}Ошибка при расчете: {e}{Style.RESET_ALL}")
            continue

        if not ask_continue():
            break


def handle_closed_multi():
    """Обработка замкнутой многоканальной СМО"""
    while True:
        print_section_header("Замкнутая многоканальная СМО")

        try:
            lambda_val, mu_val = input_lambda_mu()

            N = int(input(f"\n{Fore.GREEN}Введите количество источников (N): {Style.RESET_ALL}"))
            if N < 1:
                print(f"{Fore.RED}Ошибка: N должно быть >= 1{Style.RESET_ALL}")
                continue

            n = int(input(f"{Fore.GREEN}Введите количество каналов (n): {Style.RESET_ALL}"))
            if n < 1:
                print(f"{Fore.RED}Ошибка: n должно быть >= 1{Style.RESET_ALL}")
                continue

            # Создание системы
            system = ClosedMulti(N_sources=N, n_channels=n, lambda_val=lambda_val, mu_val=mu_val)

            # Вычисление характеристик
            results = system.calculate_all_characteristics()

            # Вывод результатов
            print_section_header("Результаты расчета")

            # Основные параметры
            params = {
                'Интенсивность источника λ': format_value(results['lambda']),
                'Интенсивность обслуживания μ': format_value(results['mu']),
                'Количество источников N': results['N_sources'],
                'Количество каналов n': results['n_channels']
            }
            print_results_table(params, "Входные параметры")

            # Вероятности состояний (первые 15)
            prob_display = {k: v for k, v in list(results['probabilities'].items())[:15]}
            print_probabilities_table(prob_display)

            # Характеристики производительности
            perf = {
                'Среднее число заявок в системе': format_value(results['avg_system_length']),
                'Средняя длина очереди': format_value(results['avg_queue_length']),
                'Эффективная интенсивность потока': format_value(results['effective_lambda']),
                'Среднее время ожидания (мин)': format_value(results['avg_wait_time']),
                'Среднее время в системе (мин)': format_value(results['avg_system_time'])
            }
            print_results_table(perf, "Характеристики производительности")

        except ValueError as e:
            print(f"{Fore.RED}Ошибка: {e}{Style.RESET_ALL}")
            continue
        except Exception as e:
            print(f"{Fore.RED}Ошибка при расчете: {e}{Style.RESET_ALL}")
            continue

        if not ask_continue():
            break


def handle_variant_18():
    """Обработка Варианта 18: Предприятие быстрого питания"""
    print_section_header("Вариант 18: Предприятие быстрого питания")

    print(f"{Fore.CYAN}Условия задачи:{Style.RESET_ALL}")
    print(f"  • Входящий поток: λ = 24 машины/час = 0.4 машины/мин")
    print(f"  • Доход на клиента: 1000 руб.")
    print(f"  • Зарплата служащего: 1000 руб./час")
    print(f"  • Стоимость канала: 20000 руб./час")
    print()

    # Входящий поток (машины в минуту)
    lambda_val = 24 / 60  # 24 машины/час = 0.4 машины/мин

    # Конфигурация 1: 1 служащий, время обслуживания 2 мин
    print(f"\n{Fore.GREEN}Конфигурация 1: 1 служащий, среднее время = 2 мин{Style.RESET_ALL}")
    mu1 = 1 / 2  # 0.5 машины/мин
    rho1 = lambda_val / mu1

    print(f"  λ = {lambda_val:.4f} машины/мин")
    print(f"  μ = {mu1:.4f} машины/мин")
    print(f"  ρ = {rho1:.4f} < 1 ✓ (система стабильна)")

    try:
        config1 = MM1inf(lambda_val=lambda_val, mu_val=mu1)
        results1 = config1.calculate_all_characteristics()
        A1 = results1['absolute_throughput']  # машины/мин
        A1_hour = A1 * 60  # машины/час

        econ1 = calculate_economic_costs(
            1, 1, 1, A1_hour,
            revenue_per_customer=1000,
            salary_per_hour=1000,
            channel_cost_per_hour=20000
        )

        print(f"  Пропускная способность: {A1:.4f} машины/мин = {A1_hour:.2f} машины/час")
        print(f"  Средняя длина очереди: {results1['avg_queue_length']:.4f}")
        print(f"  Среднее время в системе: {results1['avg_system_time']:.4f} мин")
    except Exception as e:
        print(f"  {Fore.RED}Ошибка: {e}{Style.RESET_ALL}")
        econ1 = None

    # Конфигурация 2: 2 служащих, время обслуживания 1.25 мин
    print(f"\n{Fore.GREEN}Конфигурация 2: 2 служащих, среднее время = 1.25 мин{Style.RESET_ALL}")
    mu2 = 1 / 1.25  # 0.8 машины/мин
    rho2 = lambda_val / mu2

    print(f"  λ = {lambda_val:.4f} машины/мин")
    print(f"  μ = {mu2:.4f} машины/мин")
    print(f"  ρ = {rho2:.4f} < 1 ✓ (система стабильна)")

    try:
        config2 = MM1inf(lambda_val=lambda_val, mu_val=mu2)
        results2 = config2.calculate_all_characteristics()
        A2 = results2['absolute_throughput']
        A2_hour = A2 * 60

        econ2 = calculate_economic_costs(
            2, 2, 1, A2_hour,
            revenue_per_customer=1000,
            salary_per_hour=1000,
            channel_cost_per_hour=20000
        )

        print(f"  Пропускная способность: {A2:.4f} машины/мин = {A2_hour:.2f} машины/час")
        print(f"  Средняя длина очереди: {results2['avg_queue_length']:.4f}")
        print(f"  Среднее время в системе: {results2['avg_system_time']:.4f} мин")
    except Exception as e:
        print(f"  {Fore.RED}Ошибка: {e}{Style.RESET_ALL}")
        econ2 = None

    # Конфигурация 3: 2 независимых канала, время обслуживания 2 мин каждый
    print(f"\n{Fore.GREEN}Конфигурация 3: 2 независимых канала, время = 2 мин каждый{Style.RESET_ALL}")
    mu3 = 1 / 2  # 0.5 машины/мин (для каждого канала)
    rho3 = lambda_val / mu3
    condition3 = rho3 / 2

    print(f"  λ = {lambda_val:.4f} машины/мин")
    print(f"  μ = {mu3:.4f} машины/мин (каждый канал)")
    print(f"  ρ = {rho3:.4f}, ρ/n = {condition3:.4f} < 1 ✓ (система стабильна)")

    try:
        config3 = MMninf(n_channels=2, lambda_val=lambda_val, mu_val=mu3)
        results3 = config3.calculate_all_characteristics()
        A3 = results3['absolute_throughput']
        A3_hour = A3 * 60

        econ3 = calculate_economic_costs(
            3, 2, 2, A3_hour,
            revenue_per_customer=1000,
            salary_per_hour=1000,
            channel_cost_per_hour=20000
        )

        print(f"  Пропускная способность: {A3:.4f} машины/мин = {A3_hour:.2f} машины/час")
        print(f"  Средняя длина очереди: {results3['avg_queue_length']:.4f}")
        print(f"  Среднее время в системе: {results3['avg_system_time']:.4f} мин")
    except Exception as e:
        print(f"  {Fore.RED}Ошибка: {e}{Style.RESET_ALL}")
        econ3 = None

    # Сравнение конфигураций
    print_section_header("Экономический анализ")

    if econ1 and econ2 and econ3:
        # Выводим данные в таблице
        print(f"{Fore.CYAN}{'Параметр':<40} {'Конфиг 1':<15} {'Конфиг 2':<15} {'Конфиг 3':<15}{Style.RESET_ALL}")
        print_separator('=')

        configs = [econ1, econ2, econ3]

        for config in configs:
            print(f"{Fore.YELLOW}Конфигурация {config['config_num']}: {config['n_employees']} служ., {config['n_channels']} кан.{Style.RESET_ALL}")

        print()

        print(f"{'Зарплата (руб/час)':<40} {econ1['salary_costs']:>14.0f} {econ2['salary_costs']:>14.0f} {econ3['salary_costs']:>14.0f}")
        print(f"{'Стоимость каналов (руб/час)':<40} {econ1['channel_costs']:>14.0f} {econ2['channel_costs']:>14.0f} {econ3['channel_costs']:>14.0f}")
        print(f"{'Общие затраты (руб/час)':<40} {econ1['total_costs']:>14.0f} {econ2['total_costs']:>14.0f} {econ3['total_costs']:>14.0f}")

        print()

        print(f"{'Пропускная способность (машин/час)':<40} {econ1['throughput_per_hour']:>14.2f} {econ2['throughput_per_hour']:>14.2f} {econ3['throughput_per_hour']:>14.2f}")
        print(f"{'Доход (руб/час)':<40} {econ1['revenue']:>14.0f} {econ2['revenue']:>14.0f} {econ3['revenue']:>14.0f}")
        print(f"{'Прибыль (руб/час)':<40} {econ1['profit']:>14.0f} {econ2['profit']:>14.0f} {econ3['profit']:>14.0f}")
        print(f"{'ROI (процент)':<40} {econ1['roi']:>13.1f}% {econ2['roi']:>13.1f}% {econ3['roi']:>13.1f}%")

        print_separator('=')

        # Рекомендация
        profits = [econ1['profit'], econ2['profit'], econ3['profit']]
        best_idx = profits.index(max(profits))
        best_config = best_idx + 1

        print(f"\n{Fore.GREEN}Рекомендуемая конфигурация: {best_config}{Style.RESET_ALL}")
        print(f"  Максимальная прибыль: {max(profits):,.0f} руб/час")

    input(f"\n{Fore.CYAN}Нажмите Enter для возврата в главное меню...{Style.RESET_ALL}")


def main():
    """Главная функция программы"""
    while True:
        print_main_menu()
        choice = input(f"{Fore.GREEN}Ваш выбор (1-9): {Style.RESET_ALL}").strip()

        if choice == '1':
            handle_mmn0()
        elif choice == '2':
            handle_mm1m()
        elif choice == '3':
            handle_mm1inf()
        elif choice == '4':
            handle_mmnm()
        elif choice == '5':
            handle_mmninf()
        elif choice == '6':
            handle_closed_single()
        elif choice == '7':
            handle_closed_multi()
        elif choice == '8':
            handle_variant_18()
        elif choice == '9':
            print(f"\n{Fore.CYAN}Спасибо за использование программы!{Style.RESET_ALL}\n")
            sys.exit(0)
        else:
            print(f"{Fore.RED}Ошибка: выберите пункт меню от 1 до 9{Style.RESET_ALL}")
            input("Нажмите Enter для продолжения...")


if __name__ == '__main__':
    main()
