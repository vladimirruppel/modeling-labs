#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Лабораторная работа №6
Моделирование систем по схеме марковских случайных процессов
Пуассоновские потоки событий

Вариант 18: 5 состояний марковской системы
"""

import numpy as np
from pathlib import Path
from colorama import Fore, Style, init

# Инициализируем colorama
init(autoreset=True)

# Импортируем наши модули
from utils import (
    read_lambda_matrix, print_header, print_separator,
    print_matrix, print_vector, print_check_mark
)
from kolmogorov_solver import solve_euler, print_euler_solution, choose_time_step
from steady_state_solver import solve_steady_state, print_steady_state_results
from ergodicity_checker import (
    check_ergodicity, print_ergodicity_analysis,
    modify_to_non_ergodic
)
from probability_plot import plot_probabilities_over_time, print_plot_success
from graph_visualization import draw_comparison_graphs, print_graph_success

# Константы
VARIANT = 18
DATA_DIR = Path(__file__).parent / 'data'
OUTPUT_DIR = Path(__file__).parent / 'output_charts'
FILE_DATA = DATA_DIR / f'variant_{VARIANT}.txt'


def load_data():
    """Загружает матрицу Lambda из файла."""
    Lambda = read_lambda_matrix(FILE_DATA)
    if Lambda is None:
        print(f"{Fore.RED}Не удалось загрузить данные.{Style.RESET_ALL}")
        return None
    return Lambda


def print_variant_info(Lambda):
    """Выводит информацию о варианте."""
    print_header("ПАРАМЕТРЫ ВАРИАНТА 18", 100)

    print(f"\n{Fore.CYAN}Граф состояний: 5 состояний (S₁, S₂, S₃, S₄, S₅){Style.RESET_ALL}")
    print(f"\nПереходы и их интенсивности:")
    print_separator("-", 100)

    # Выписываем все ненулевые переходы
    transitions = []
    for i in range(5):
        for j in range(5):
            if i != j and abs(Lambda[i][j]) > 1e-10:
                transitions.append((i+1, j+1, Lambda[i][j]))

    for i_state, j_state, intensity in sorted(transitions):
        print(f"  S{i_state} → S{j_state}: λ = {intensity:>6.1f}")

    print_separator("-", 100)

    print(f"\n{Fore.CYAN}Матрица интенсивностей Λ:{Style.RESET_ALL}")
    print_matrix(Lambda, "Λ")

    # Вычисляем и выводим информацию о шаге
    print(f"\n{Fore.CYAN}Информация о методе Эйлера:{Style.RESET_ALL}")
    step_info = choose_time_step(Lambda)
    print(step_info['info'])


def run_task_1_full_analysis(Lambda):
    """Опция 1: Полный анализ (все пункты)."""
    print_header("ПОЛНЫЙ АНАЛИЗ", 100)

    # 1. Параметры варианта
    print_variant_info(Lambda)

    # 2. Численное решение
    print("\n")
    input(f"{Fore.YELLOW}Нажмите Enter для численного решения...{Style.RESET_ALL}")
    solution_data = solve_euler(Lambda)
    print_euler_solution(Lambda, solution_data)

    # 3. Предельные вероятности
    print("\n")
    input(f"{Fore.YELLOW}Нажмите Enter для вычисления предельных вероятностей...{Style.RESET_ALL}")
    steady_state_data = solve_steady_state(Lambda)
    print_steady_state_results(steady_state_data)

    # 4. Проверка эргодичности
    print("\n")
    input(f"{Fore.YELLOW}Нажмите Enter для проверки эргодичности...{Style.RESET_ALL}")
    ergodicity_data = check_ergodicity(Lambda)
    print_ergodicity_analysis(ergodicity_data)

    # 5. Графики
    print("\n")
    input(f"{Fore.YELLOW}Нажмите Enter для построения графиков...{Style.RESET_ALL}")

    # График вероятностей
    graph_path = plot_probabilities_over_time(
        solution_data['times'],
        solution_data['probabilities'],
        steady_state=steady_state_data,
        output_file=str(OUTPUT_DIR / "probabilities_over_time.png")
    )
    print_plot_success(graph_path)

    # Графы состояний
    if ergodicity_data['is_ergodic']:
        # Модифицируем граф для создания неэргодичной системы
        print(f"\n{Fore.CYAN}Граф эргодичен. Модифицируем его для создания неэргодичной системы...{Style.RESET_ALL}")

        Lambda_modified = modify_to_non_ergodic(Lambda)

        # Рисуем оба графа
        path_orig, path_mod = draw_comparison_graphs(Lambda, Lambda_modified)
        print_graph_success(path_orig)
        print_graph_success(path_mod)

        # Решение для модифицированной системы
        print("\n")
        input(f"{Fore.YELLOW}Нажмите Enter для анализа модифицированной системы...{Style.RESET_ALL}")

        print_header("МОДИФИЦИРОВАННАЯ (НЕЭРГОДИЧНАЯ) СИСТЕМА", 100)

        # Численное решение для модифицированной системы
        solution_mod = solve_euler(Lambda_modified)
        print_euler_solution(Lambda_modified, solution_mod)

        # Предельные вероятности для модифицированной системы
        print("\n")
        steady_state_mod = solve_steady_state(Lambda_modified)
        print_steady_state_results(steady_state_mod)

        # Проверка эргодичности модифицированной системы
        print("\n")
        ergodicity_mod = check_ergodicity(Lambda_modified)
        print_ergodicity_analysis(ergodicity_mod)

    else:
        # Граф уже неэргодичен
        path_orig, _ = draw_comparison_graphs(Lambda)
        print_graph_success(path_orig)
        print(f"{Fore.GREEN}✓ Исходный граф уже неэргодичен!{Style.RESET_ALL}")


def run_task_2_show_params(Lambda):
    """Опция 2: Показать параметры варианта."""
    print_variant_info(Lambda)


def run_task_3_solve_euler(Lambda):
    """Опция 3: Численное решение."""
    print_header("ЧИСЛЕННОЕ РЕШЕНИЕ МЕТОДОМ ЭЙЛЕРА", 100)
    solution_data = solve_euler(Lambda)
    print_euler_solution(Lambda, solution_data)


def run_task_4_plot(Lambda):
    """Опция 4: Графики вероятностей."""
    print_header("ПОСТРОЕНИЕ ГРАФИКОВ", 100)

    solution_data = solve_euler(Lambda)
    steady_state_data = solve_steady_state(Lambda)

    print(f"{Fore.CYAN}Построение графика вероятностей p_i(t)...{Style.RESET_ALL}")

    graph_path = plot_probabilities_over_time(
        solution_data['times'],
        solution_data['probabilities'],
        steady_state=steady_state_data,
        output_file=str(OUTPUT_DIR / "probabilities_over_time.png")
    )
    print_plot_success(graph_path)


def run_task_5_steady_state(Lambda):
    """Опция 5: Предельные вероятности."""
    print_header("ПРЕДЕЛЬНЫЕ ВЕРОЯТНОСТИ", 100)
    steady_state_data = solve_steady_state(Lambda)
    print_steady_state_results(steady_state_data)


def run_task_6_ergodicity(Lambda):
    """Опция 6: Проверка эргодичности."""
    print_header("ПРОВЕРКА ЭРГОДИЧНОСТИ", 100)
    ergodicity_data = check_ergodicity(Lambda)
    print_ergodicity_analysis(ergodicity_data)


def run_task_7_modify_graph(Lambda):
    """Опция 7: Модификация графа (создание неэргодичной системы)."""
    print_header("МОДИФИКАЦИЯ ГРАФА", 100)

    # Проверяем исходную эргодичность
    ergodicity_orig = check_ergodicity(Lambda)

    if ergodicity_orig['is_ergodic']:
        print(f"{Fore.CYAN}Исходная система эргодична. Модифицируем граф...{Style.RESET_ALL}\n")

        # Модифицируем
        Lambda_modified = modify_to_non_ergodic(Lambda)

        # Выводим информацию о модификации
        print(f"{Fore.CYAN}Стратегия модификации:{Style.RESET_ALL}")
        print("  • Разделяем состояния на два класса:")
        print("    - Класс 1: S₁, S₂")
        print("    - Класс 2: S₃, S₄, S₅")
        print("  • Обнулляем переходы между классами\n")

        # Проверяем модифицированную систему
        ergodicity_mod = check_ergodicity(Lambda_modified)

        print(f"{Fore.CYAN}Проверка модифицированной системы:{Style.RESET_ALL}")
        print_ergodicity_analysis(ergodicity_mod)

        # Графы
        print(f"\n{Fore.CYAN}Рисуем графы состояний...{Style.RESET_ALL}")
        path_orig, path_mod = draw_comparison_graphs(Lambda, Lambda_modified)
        print_graph_success(path_orig)
        print_graph_success(path_mod)

    else:
        print(f"{Fore.GREEN}Система уже неэргодична!{Style.RESET_ALL}")
        print_ergodicity_analysis(ergodicity_orig)


def main_menu():
    """Главное интерактивное меню."""
    # Загружаем данные
    Lambda = load_data()
    if Lambda is None:
        return

    while True:
        # Очищаем экран и выводим меню
        print("\n" + "="*100)
        print(f"{Fore.CYAN}ЛАБОРАТОРНАЯ РАБОТА №6{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Марковские случайные процессы (Вариант {VARIANT}){Style.RESET_ALL}")
        print("="*100)
        print(f"""
{Fore.GREEN}1.  Полный анализ (все пункты){Style.RESET_ALL}
{Fore.GREEN}2.  Показать параметры варианта{Style.RESET_ALL}
{Fore.GREEN}3.  Численное решение (метод Эйлера){Style.RESET_ALL}
{Fore.GREEN}4.  Графики вероятностей{Style.RESET_ALL}
{Fore.GREEN}5.  Предельные вероятности{Style.RESET_ALL}
{Fore.GREEN}6.  Проверка эргодичности{Style.RESET_ALL}
{Fore.GREEN}7.  Модификация графа (неэргодичная система){Style.RESET_ALL}
{Fore.RED}0.  Выход{Style.RESET_ALL}
""")
        print("="*100)

        choice = input(f"{Fore.YELLOW}Выберите пункт меню (0-7): {Style.RESET_ALL}").strip()

        if choice == '1':
            run_task_1_full_analysis(Lambda)
        elif choice == '2':
            run_task_2_show_params(Lambda)
        elif choice == '3':
            run_task_3_solve_euler(Lambda)
        elif choice == '4':
            run_task_4_plot(Lambda)
        elif choice == '5':
            run_task_5_steady_state(Lambda)
        elif choice == '6':
            run_task_6_ergodicity(Lambda)
        elif choice == '7':
            run_task_7_modify_graph(Lambda)
        elif choice == '0':
            print(f"{Fore.GREEN}Спасибо за использование программы. Выход.{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED}Неверный ввод. Пожалуйста, выберите пункт 0-7.{Style.RESET_ALL}")

        # Пауза перед возвратом в меню
        input(f"\n{Fore.YELLOW}Нажмите Enter для возврата в меню...{Style.RESET_ALL}")


if __name__ == "__main__":
    main_menu()
