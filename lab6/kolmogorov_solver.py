"""
Численное решение системы уравнений Колмогорова методом Эйлера.
Реализует метод P_{k+1} = (I + h*Lambda) * P_k
"""

import numpy as np
from colorama import Fore, Style
from utils import print_header, print_matrix, print_vector, print_solution_table, print_check_mark, print_separator


def choose_time_step(Lambda, safety_factor=0.6):
    """
    Выбор шага времени h для метода Эйлера.

    Условие устойчивости: собственные числа матрицы (I + h*Lambda)
    должны быть по модулю меньше 1.

    Args:
        Lambda: матрица интенсивностей (5x5)
        safety_factor: коэффициент безопасности (по умолчанию 0.8)

    Returns:
        dict с ключами:
            'h': выбранный шаг времени
            'eigenvalues': собственные числа Lambda
            'max_eigenvalue': max|lambda|
            'h_max': теоретический максимум h
            'info': строковое объяснение выбора
    """
    # Вычисляем собственные числа
    eigenvalues = np.linalg.eigvals(Lambda)

    # Находим максимум по модулю
    max_abs_eigenvalue = np.max(np.abs(eigenvalues))

    # Теоретический максимум шага: h < 2 / max|lambda|
    h_max = 2.0 / max_abs_eigenvalue

    # Выбираем h с запасом безопасности
    h = safety_factor * h_max

    info = f"""
Выбор шага времени h:
  • Собственные числа Λ: {[f'{ev:.2f}' for ev in eigenvalues]}
  • max|λ| = {max_abs_eigenvalue:.2f}
  • Теоретическое ограничение: h < 2/{max_abs_eigenvalue:.2f} = {h_max:.4f}
  • Выбранный шаг: h = {safety_factor} × {h_max:.4f} = {h:.4f}
  • Условие устойчивости: |λ_i × h| < 1 для всех i ✓
"""

    return {
        'h': h,
        'eigenvalues': eigenvalues,
        'max_eigenvalue': max_abs_eigenvalue,
        'h_max': h_max,
        'info': info
    }


def solve_euler(Lambda, P0=None, t_max=15.0, h=None, convergence_tol=1e-6):
    """
    Решение системы уравнений Колмогорова методом Эйлера.

    Метод: P_{k+1} = (I + h*Lambda) * P_k

    Args:
        Lambda: матрица интенсивностей (5x5)
        P0: начальные условия (по умолчанию [1, 0, 0, 0, 0])
        t_max: максимальное время интегрирования
        h: шаг времени (если None, вычисляется автоматически)
        convergence_tol: допуск для определения сходимости

    Returns:
        dict с ключами:
            'times': список времён t_k
            'probabilities': список векторов P_k
            'num_steps': количество шагов
            'converged': сошлась ли система
            'convergence_step': шаг, на котором произошла сходимость
            'step_size': использованный шаг h
    """
    # Начальные условия
    if P0 is None:
        P0 = np.array([1.0, 0.0, 0.0, 0.0, 0.0])
    else:
        P0 = np.array(P0, dtype=float)

    # Выбираем шаг времени если не задан
    if h is None:
        step_info = choose_time_step(Lambda)
        h = step_info['h']

    # Построение матрицы A = I + h*Lambda
    I = np.eye(5)
    A = I + h * Lambda

    # Проверяем устойчивость
    eigenvalues_A = np.linalg.eigvals(A)
    max_abs_eigenvalue_A = np.max(np.abs(eigenvalues_A))

    if max_abs_eigenvalue_A >= 1.0:
        print(f"{Fore.YELLOW}Предупреждение: max|λ_A| = {max_abs_eigenvalue_A:.4f} >= 1")
        print(f"Метод может быть неустойчив!{Style.RESET_ALL}")

    # Численное интегрирование
    times = [0.0]
    probabilities = [P0.copy()]
    P = P0.copy()
    t = 0.0
    k = 0
    converged = False
    convergence_step = None

    while t < t_max:
        # Эйлеров шаг: P_new = A @ P
        P_new = A @ P

        # Нормализация (корректировка ошибок округления)
        P_new = P_new / np.sum(P_new)

        # Проверка сходимости
        diff = np.linalg.norm(P_new - P)
        if diff < convergence_tol:
            converged = True
            convergence_step = k
            # Добавляем последний шаг и выходим
            times.append(t + h)
            probabilities.append(P_new)
            break

        # Переход к следующему шагу
        P = P_new
        t += h
        k += 1

        times.append(t)
        probabilities.append(P.copy())

    return {
        'times': np.array(times),
        'probabilities': np.array(probabilities),
        'num_steps': len(times),
        'converged': converged,
        'convergence_step': convergence_step,
        'step_size': h
    }


def print_euler_solution(Lambda, solution_data):
    """
    Красиво выводит результаты численного решения.

    Args:
        Lambda: матрица интенсивностей
        solution_data: результаты solve_euler()
    """
    print_header("ЧИСЛЕННОЕ РЕШЕНИЕ МЕТОДОМ ЭЙЛЕРА", 100)

    # Информация о выборе шага
    step_info = choose_time_step(Lambda, safety_factor=0.8)
    print(step_info['info'])

    # Начальные условия
    print(f"\n{Fore.CYAN}Начальные условия:{Style.RESET_ALL}")
    print("  p₁(0) = 1")
    print("  p₂(0) = 0")
    print("  p₃(0) = 0")
    print("  p₄(0) = 0")
    print("  p₅(0) = 0\n")

    # Таблица с решением
    print_solution_table(solution_data['times'], solution_data['probabilities'], max_rows=20)

    # Статус сходимости
    print()
    if solution_data['converged']:
        print_check_mark(
            True,
            f"Система сошлась за {solution_data['convergence_step']} шагов "
            f"(t ≈ {solution_data['times'][solution_data['convergence_step']]:.3f})"
        )
    else:
        print_check_mark(
            False,
            f"Система не сошлась в пределах {solution_data['num_steps']} шагов"
        )

    # Предельные значения
    print(f"\n{Fore.CYAN}Предельные значения (конец переходного режима):{Style.RESET_ALL}")
    P_final = solution_data['probabilities'][-1]
    for i, p in enumerate(P_final, 1):
        print(f"  p{i} ≈ {p:.6f}")
