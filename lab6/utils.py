"""
Утилиты для работы с данными и форматирования вывода.
Функции для чтения матрицы Lambda, печати таблиц и результатов.
"""

import numpy as np
from colorama import Fore, Style
from pathlib import Path


def read_lambda_matrix(filepath):
    """
    Читает матрицу интенсивностей Lambda из файла.

    Args:
        filepath: путь к файлу с матрицей

    Returns:
        numpy array (5x5) или None в случае ошибки
    """
    try:
        # Читаем файл, пропуская строки с комментариями
        data = []
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    row = list(map(float, line.split()))
                    data.append(row)

        if not data:
            print(f"{Fore.RED}Ошибка: Файл пуст или не содержит числовых данных.{Style.RESET_ALL}")
            return None

        Lambda = np.array(data)

        if Lambda.shape != (5, 5):
            print(f"{Fore.RED}Ошибка: Матрица должна быть 5x5, получена {Lambda.shape}{Style.RESET_ALL}")
            return None

        return Lambda

    except FileNotFoundError:
        print(f"{Fore.RED}Ошибка: Файл {filepath} не найден.{Style.RESET_ALL}")
        return None
    except ValueError as e:
        print(f"{Fore.RED}Ошибка при чтении данных: {e}{Style.RESET_ALL}")
        return None


def print_separator(char="=", width=80):
    """Печатает разделитель."""
    print(char * width)


def print_header(title, width=80):
    """Печатает заголовок секции."""
    print_separator("=", width)
    print(f"{Fore.CYAN}{title.center(width)}{Style.RESET_ALL}")
    print_separator("=", width)


def print_matrix(matrix, title="Матрица", width=80):
    """
    Красиво печатает матрицу.

    Args:
        matrix: numpy array
        title: название матрицы
        width: ширина вывода
    """
    print(f"\n{Fore.CYAN}{title}:{Style.RESET_ALL}")
    print("-" * width)

    # Определяем ширину каждого столбца
    col_width = 10

    # Печатаем строки матрицы
    for i, row in enumerate(matrix):
        row_str = f"[{i+1}]  "
        for val in row:
            row_str += f"{val:>10.2f}  "
        print(row_str)

    print("-" * width)


def print_vector(vector, labels=None, title="Вектор", width=80):
    """
    Красиво печатает вектор.

    Args:
        vector: список или numpy array
        labels: список подписей (по умолчанию p1, p2, ...)
        title: название вектора
        width: ширина вывода
    """
    print(f"\n{Fore.CYAN}{title}:{Style.RESET_ALL}")
    print("-" * width)

    if labels is None:
        labels = [f"p{i+1}" for i in range(len(vector))]

    for label, val in zip(labels, vector):
        print(f"  {label:>5} = {val:>10.6f}")

    print("-" * width)


def print_solution_table(times, probabilities, max_rows=20):
    """
    Печатает таблицу численного решения.

    Args:
        times: список времён
        probabilities: список векторов вероятностей
        max_rows: максимум строк для вывода (показывает первые и последние)
    """
    n_steps = len(times)
    print_separator("-", 100)

    # Заголовок таблицы
    header = " Шаг  |   t    |   p₁(t)  |   p₂(t)  |   p₃(t)  |   p₄(t)  |   p₅(t)  |  Σp_i"
    print(header)
    print_separator("-", 100)

    # Определяем, сколько строк показывать сверху и снизу
    if n_steps <= max_rows:
        rows_to_show = list(range(n_steps))
    else:
        top_rows = max_rows // 2
        bottom_rows = max_rows - top_rows
        rows_to_show = list(range(top_rows)) + list(range(n_steps - bottom_rows, n_steps))

    prev_row_idx = -2
    for row_idx in rows_to_show:
        # Добавляем разделитель если пропускаем строки
        if row_idx > prev_row_idx + 1:
            print(f"  ...  |  ...   |   ...    |   ...    |   ...    |   ...    |   ...    |  ...")

        t = times[row_idx]
        p = probabilities[row_idx]
        p_sum = sum(p)

        print(f" {row_idx:>4d} | {t:>6.3f} | {p[0]:>8.4f} | {p[1]:>8.4f} | {p[2]:>8.4f} | {p[3]:>8.4f} | {p[4]:>8.4f} | {p_sum:>6.4f}")
        prev_row_idx = row_idx

    print_separator("-", 100)
    print(f"{Fore.YELLOW}Всего шагов: {n_steps}{Style.RESET_ALL}")


def verify_probabilities(probabilities, tolerance=1e-6):
    """
    Проверяет корректность вероятностей (сумма должна быть 1).

    Args:
        probabilities: список векторов вероятностей
        tolerance: допуск ошибки

    Returns:
        tuple (is_valid, max_error)
    """
    max_error = 0
    for p in probabilities:
        error = abs(sum(p) - 1.0)
        max_error = max(max_error, error)
        if error > tolerance:
            return False, max_error

    return True, max_error


def print_check_mark(condition, message_true, message_false=""):
    """
    Печатает сообщение с галочкой или крестиком.

    Args:
        condition: булево значение
        message_true: сообщение если true
        message_false: сообщение если false
    """
    if condition:
        print(f"{Fore.GREEN}✓ {message_true}{Style.RESET_ALL}")
    else:
        msg = message_false if message_false else message_true
        print(f"{Fore.RED}✗ {msg}{Style.RESET_ALL}")
