"""
Проверка эргодичности марковской системы.
Анализирует достижимость состояний и модифицирует граф для создания неэргодичной системы.
"""

import numpy as np
from colorama import Fore, Style
from utils import print_header, print_matrix, print_check_mark, print_separator


def check_ergodicity(Lambda, tolerance=1e-10):
    """
    Проверяет эргодичность системы через матрицу достижимости (Флойд-Уоршелл).

    Система эргодична, если из любого состояния можно достичь любое другое состояние,
    и предельные вероятности не зависят от начальных условий.

    Алгоритм:
    1. Построить матрицу смежности: adj[i][j] = 1 если λ_ij > 0
    2. Вычислить матрицу достижимости (транзитивное замыкание)
    3. Система эргодична ⟺ все элементы = 1

    Args:
        Lambda: матрица интенсивностей (5x5)
        tolerance: допуск для сравнения с нулём

    Returns:
        dict с ключами:
            'is_ergodic': True если система эргодична
            'adjacency_matrix': матрица смежности (есть ли переходы)
            'reachability_matrix': матрица достижимости
            'communicating_classes': список классов эквивалентности
            'transient_states': переходные состояния
            'recurrent_states': возвратные состояния
            'info': описание результата
    """
    n = 5

    # Строим матрицу смежности (есть ли переходы)
    adjacency = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(n):
            if abs(Lambda[i][j]) > tolerance and i != j:
                adjacency[i][j] = 1
            elif i == j:
                # Диагональные элементы (переход в себя) - проверяем Lambda[i][i] < 0
                pass

    # Каждое состояние достижимо из себя
    reachability = adjacency.copy()
    for i in range(n):
        reachability[i][i] = 1

    # Флойд-Уоршелл для вычисления транзитивного замыкания
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if reachability[i][k] and reachability[k][j]:
                    reachability[i][j] = 1

    # Проверка эргодичности
    is_ergodic = np.all(reachability == 1)

    # Поиск классов эквивалентности
    communicating_classes = find_communicating_classes(reachability)

    # Поиск переходных и возвратных состояний
    transient_states = []
    recurrent_states = []

    for i in range(n):
        # Состояние i возвратно, если из i можно вернуться в i
        is_recurrent = reachability[i][i] == 1 and all(reachability[j][i] for j in range(n) if reachability[i][j])

        # Более точная проверка: состояние возвратно, если оно принадлежит коммуникативному классу
        # и все состояния класса достижимы друг из друга
        is_in_closed_class = False
        for cls in communicating_classes:
            if i in cls:
                # Класс замкнут если из любого состояния класса нельзя выйти
                is_closed = all(reachability[i][j] == 0 or j in cls for j in range(n) for i_cls in cls)
                if is_closed:
                    is_in_closed_class = True
                break

        if is_in_closed_class:
            recurrent_states.append(i)
        else:
            transient_states.append(i)

    info = f"""
Анализ эргодичности:
  • Эргодичность: {'ДА' if is_ergodic else 'НЕТ'}
  • Коммуникативные классы: {communicating_classes}
  • Возвратные состояния: {[i+1 for i in recurrent_states]}
  • Переходные состояния: {[i+1 for i in transient_states]}
"""

    return {
        'is_ergodic': is_ergodic,
        'adjacency_matrix': adjacency,
        'reachability_matrix': reachability,
        'communicating_classes': communicating_classes,
        'transient_states': transient_states,
        'recurrent_states': recurrent_states,
        'info': info
    }


def find_communicating_classes(reachability):
    """
    Находит коммуникативные классы (классы эквивалентности).

    Два состояния эквивалентны, если они достижимы друг из друга.

    Args:
        reachability: матрица достижимости

    Returns:
        список списков (каждый подсписок - один класс)
    """
    n = len(reachability)
    visited = [False] * n
    classes = []

    for i in range(n):
        if not visited[i]:
            # Найти все состояния, эквивалентные i
            current_class = []
            for j in range(n):
                if reachability[i][j] and reachability[j][i]:
                    current_class.append(j)
                    visited[j] = True

            if current_class:
                classes.append(current_class)

    return classes


def modify_to_non_ergodic(Lambda):
    """
    Модифицирует граф для создания неэргодичной системы.

    Стратегия: создаем два изолированных класса состояний
    - Класс 1: {S₁, S₂}
    - Класс 2: {S₃, S₄, S₅}
    Удаляем все переходы из класса 1 в класс 2 и наоборот.

    Args:
        Lambda: исходная матрица интенсивностей

    Returns:
        модифицированная матрица
    """
    Lambda_mod = Lambda.copy()

    # Класс 1: состояния 0, 1 (S₁, S₂)
    # Класс 2: состояния 2, 3, 4 (S₃, S₄, S₅)

    class1 = [0, 1]
    class2 = [2, 3, 4]

    # Обнулляем переходы между классами
    for i in class1:
        for j in class2:
            Lambda_mod[i][j] = 0
    for i in class2:
        for j in class1:
            Lambda_mod[i][j] = 0

    # Пересчитываем диагональные элементы (λ_ii = -Σ λ_ij для j≠i)
    for i in range(5):
        Lambda_mod[i][i] = -np.sum([Lambda_mod[i][j] for j in range(5) if j != i])

    return Lambda_mod


def print_ergodicity_analysis(ergodicity_data):
    """
    Выводит результаты анализа эргодичности.

    Args:
        ergodicity_data: результаты check_ergodicity()
    """
    print_header("АНАЛИЗ ЭРГОДИЧНОСТИ", 100)

    print(f"\n{Fore.CYAN}Матрица достижимости (reach[i,j]=1 если из S_i можно достичь S_j):{Style.RESET_ALL}")
    print_matrix(ergodicity_data['reachability_matrix'], "Матрица достижимости R")

    print(f"\n{Fore.CYAN}Результаты анализа:{Style.RESET_ALL}")
    print_separator("-", 80)

    # Эргодичность
    print_check_mark(
        ergodicity_data['is_ergodic'],
        "Система ЭРГОДИЧНА (из любого состояния можно достичь любое другое)",
        "Система НЕ эргодична (есть изолированные классы состояний)"
    )

    # Коммуникативные классы
    classes = ergodicity_data['communicating_classes']
    print(f"\n{Fore.CYAN}Коммуникативные классы:{Style.RESET_ALL}")
    for i, cls in enumerate(classes, 1):
        states_str = " ↔ ".join([f"S{j+1}" for j in sorted(cls)])
        print(f"  Класс {i}: {states_str}")

    print_separator("-", 80)
