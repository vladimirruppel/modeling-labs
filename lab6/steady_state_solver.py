"""
Решение для предельных (стационарных) вероятностей.
Решает систему Λ'·P = B, где в последней строке стоит условие нормировки.
"""

import numpy as np
from colorama import Fore, Style
from utils import print_header, print_vector, print_check_mark, print_separator


def solve_steady_state(Lambda):
    """
    Вычисляет предельные вероятности из условия установившегося режима.

    Теория:
    - В установившемском режиме: dp_i/dt = 0
    - Система: Λ·P = 0 (однородная система)
    - Добавляем условие нормировки: Σp_i = 1

    Алгоритм:
    1. A = Λ (исходная матрица)
    2. Заменяем последнюю строку на [1, 1, 1, 1, 1]
    3. B = [0, 0, 0, 0, 1]
    4. Решаем A·P = B методом Гаусса

    Args:
        Lambda: матрица интенсивностей (5x5)

    Returns:
        dict с ключами:
            'probabilities': вектор предельных вероятностей
            'error_check': норма Λ·P (должна быть близка к 0)
            'sum_check': сумма P (должна быть 1)
            'is_valid': корректно ли решение
    """
    # Готовим систему СЛАУ: берем матрицу Λ напрямую
    A = Lambda.copy()
    A[-1] = np.ones(5)

    # Правая часть системы
    B = np.zeros(5)
    B[-1] = 1.0

    try:
        # Решаем СЛАУ методом Гаусса (np.linalg.solve)
        P_steady = np.linalg.solve(A, B)

        # Проверка корректности
        # 1. Сумма должна быть 1
        sum_check = np.sum(P_steady)

        # 2. Λ·P должно быть близко к нулю
        error_check = np.linalg.norm(Lambda @ P_steady)

        # 3. Все вероятности должны быть неотрицательны
        all_positive = np.all(P_steady >= -1e-10)  # допускаем небольшую ошибку округления

        is_valid = (abs(sum_check - 1.0) < 1e-6) and (error_check < 1e-6) and all_positive

        return {
            'probabilities': P_steady,
            'error_check': error_check,
            'sum_check': sum_check,
            'is_valid': is_valid
        }

    except np.linalg.LinAlgError as e:
        print(f"{Fore.RED}Ошибка при решении СЛАУ: {e}{Style.RESET_ALL}")
        return None


def print_steady_state_results(solution_data):
    """
    Красиво выводит результаты для предельных вероятностей.

    Args:
        solution_data: результаты solve_steady_state()
    """
    print_header("ПРЕДЕЛЬНЫЕ ВЕРОЯТНОСТИ", 80)

    if solution_data is None:
        print(f"{Fore.RED}Ошибка: не удалось решить систему.{Style.RESET_ALL}")
        return

    P_steady = solution_data['probabilities']

    # Печатаем значения
    print(f"\n{Fore.CYAN}Значения предельных вероятностей:{Style.RESET_ALL}")
    print("-" * 50)
    for i, p in enumerate(P_steady, 1):
        print(f"  p{i}* = {p:>10.6f}")
    print("-" * 50)

    # Проверки
    print(f"\n{Fore.CYAN}Проверка корректности:{Style.RESET_ALL}")
    print_separator("-", 50)

    # Проверка 1: сумма вероятностей = 1
    sum_p = solution_data['sum_check']
    print_check_mark(
        abs(sum_p - 1.0) < 1e-6,
        f"Σp_i* = {sum_p:.10f} ≈ 1.0"
    )

    # Проверка 2: Λ·P* ≈ 0
    error = solution_data['error_check']
    print_check_mark(
        error < 1e-5,
        f"||Λ·P*|| = {error:.2e} ≈ 0",
        f"||Λ·P*|| = {error:.2e} (ошибка слишком велика)"
    )

    # Проверка 3: все вероятности неотрицательны
    all_positive = np.all(P_steady >= -1e-10)
    print_check_mark(
        all_positive,
        "Все p_i* ≥ 0"
    )

    # Общий результат
    print()
    if solution_data['is_valid']:
        print(f"{Fore.GREEN}✓ Решение корректно!{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠ Решение имеет проблемы с корректностью{Style.RESET_ALL}")

    print_separator("-", 50)
