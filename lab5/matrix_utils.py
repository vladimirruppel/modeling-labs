"""
Утилиты для работы с матрицами в алгоритме Литтла
"""
import copy
from typing import Tuple, List, Optional
import math


class MatrixOperations:
    """Операции над матрицами затрат"""

    INF = 999  # Бесконечность в представлении

    @staticmethod
    def reduce_rows(matrix: List[List[int]]) -> Tuple[List[List[int]], int]:
        """
        Приведение строк матрицы (вычитание минимума каждой строки)

        Args:
            matrix: Исходная матрица

        Returns:
            Кортеж (приведённая матрица, сумма вычтенных значений)
        """
        result = copy.deepcopy(matrix)
        row_reductions = []
        total_reduction = 0

        for i in range(len(matrix)):
            # Найти минимум в строке (исключая бесконечности)
            row_values = [matrix[i][j] for j in range(len(matrix[i]))
                         if matrix[i][j] != MatrixOperations.INF]

            if not row_values:
                continue

            min_val = min(row_values)
            row_reductions.append(min_val)
            total_reduction += min_val

            # Вычесть минимум из строки
            for j in range(len(result[i])):
                if result[i][j] != MatrixOperations.INF:
                    result[i][j] -= min_val

        return result, total_reduction

    @staticmethod
    def reduce_columns(matrix: List[List[int]]) -> Tuple[List[List[int]], int]:
        """
        Приведение столбцов матрицы (вычитание минимума каждого столбца)

        Args:
            matrix: Исходная матрица

        Returns:
            Кортеж (приведённая матрица, сумма вычтенных значений)
        """
        result = copy.deepcopy(matrix)
        col_reductions = []
        total_reduction = 0
        n = len(matrix)

        for j in range(n):
            # Найти минимум в столбце (исключая бесконечности)
            col_values = [matrix[i][j] for i in range(n)
                         if matrix[i][j] != MatrixOperations.INF]

            if not col_values:
                continue

            min_val = min(col_values)
            col_reductions.append(min_val)
            total_reduction += min_val

            # Вычесть минимум из столбца
            for i in range(n):
                if result[i][j] != MatrixOperations.INF:
                    result[i][j] -= min_val

        return result, total_reduction

    @staticmethod
    def full_reduction(matrix: List[List[int]]) -> Tuple[List[List[int]], int]:
        """
        Полное приведение матрицы (строки + столбцы)

        Args:
            matrix: Исходная матрица

        Returns:
            Кортеж (полностью приведённая матрица, сумма всех приведений)
        """
        reduced_rows, row_reduction = MatrixOperations.reduce_rows(matrix)
        reduced_all, col_reduction = MatrixOperations.reduce_columns(reduced_rows)

        total_reduction = row_reduction + col_reduction
        return reduced_all, total_reduction

    @staticmethod
    def calculate_penalties(matrix: List[List[int]]) -> dict:
        """
        Вычисление штрафов за неиспользование нулей

        Args:
            matrix: Приведённая матрица (с нулями на диагонали исключенных рёбер)

        Returns:
            Словарь {(i, j): штраф} для всех нулей в матрице
        """
        penalties = {}
        n = len(matrix)

        for i in range(n):
            for j in range(n):
                if matrix[i][j] == 0:
                    # Найти минимум в строке i, исключая элемент (i, j)
                    row_min = float('inf')
                    for k in range(n):
                        if k != j and matrix[i][k] != MatrixOperations.INF:
                            row_min = min(row_min, matrix[i][k])

                    # Найти минимум в столбце j, исключая элемент (i, j)
                    col_min = float('inf')
                    for k in range(n):
                        if k != i and matrix[k][j] != MatrixOperations.INF:
                            col_min = min(col_min, matrix[k][j])

                    # Штраф = минимум из строки + минимум из столбца
                    penalty = 0
                    if row_min != float('inf'):
                        penalty += row_min
                    if col_min != float('inf'):
                        penalty += col_min

                    penalties[(i, j)] = penalty

        return penalties

    @staticmethod
    def create_reduced_matrix(matrix: List[List[int]],
                             edge_i: int, edge_j: int) -> List[List[int]]:
        """
        Создание редуцированной матрицы после выбора ребра (i, j)

        Args:
            matrix: Исходная матрица
            edge_i: Первый город
            edge_j: Второй город

        Returns:
            Матрица с блокированным обратным ребром и удалённой строкой/столбцом
        """
        # Сначала блокируем обратное ребро
        result = copy.deepcopy(matrix)
        result[edge_j][edge_i] = MatrixOperations.INF

        # Удаляем строку edge_i и столбец edge_j
        reduced = []
        for i in range(len(result)):
            if i != edge_i:
                row = []
                for j in range(len(result[i])):
                    if j != edge_j:
                        row.append(result[i][j])
                reduced.append(row)

        return reduced

    @staticmethod
    def is_valid_matrix(matrix: List[List[int]]) -> bool:
        """
        Проверка валидности матрицы (есть ли конечные элементы в каждой строке/столбце)

        Args:
            matrix: Матрица для проверки

        Returns:
            True если матрица валидна, False иначе
        """
        if not matrix or len(matrix) == 0:
            return True  # Пустая матрица валидна (базовый случай)

        # Проверяем, есть ли в каждой строке хотя бы один конечный элемент
        for i in range(len(matrix)):
            has_finite = False
            for j in range(len(matrix[i])):
                if matrix[i][j] != MatrixOperations.INF:
                    has_finite = True
                    break
            if not has_finite:
                return False

        # Проверяем, есть ли в каждом столбце хотя бы один конечный элемент
        n = len(matrix)
        if n > 0:
            for j in range(len(matrix[0])):
                has_finite = False
                for i in range(n):
                    if matrix[i][j] != MatrixOperations.INF:
                        has_finite = True
                        break
                if not has_finite:
                    return False

        return True

    @staticmethod
    def format_matrix(matrix: List[List[int]],
                     digits: int = 4) -> str:
        """
        Форматирование матрицы для красивого вывода

        Args:
            matrix: Матрица для вывода
            digits: Ширина каждого элемента

        Returns:
            Отформатированная строка с матрицей
        """
        if not matrix:
            return "Пустая матрица"

        result = []
        for row in matrix:
            formatted_row = []
            for val in row:
                if val == MatrixOperations.INF:
                    formatted_row.append("∞".rjust(digits))
                else:
                    formatted_row.append(str(val).rjust(digits))
            result.append(" ".join(formatted_row))

        return "\n".join(result)

    @staticmethod
    def calculate_tour_cost(cost_matrix: List[List[int]],
                           tour: List[int]) -> int:
        """
        Вычисление стоимости маршрута

        Args:
            cost_matrix: Исходная матрица затрат
            tour: Маршрут (последовательность городов)

        Returns:
            Общая стоимость маршрута
        """
        total_cost = 0
        n = len(tour)

        for i in range(n):
            from_city = tour[i]
            to_city = tour[(i + 1) % n]
            total_cost += cost_matrix[from_city][to_city]

        return total_cost
