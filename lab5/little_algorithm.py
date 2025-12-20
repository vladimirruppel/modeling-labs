"""
Реализация алгоритма Литтла для решения задачи коммивояжера
Метод ветвей и границ (Branch and Bound)
"""
import copy
from typing import List, Tuple, Optional, Set
from matrix_utils import MatrixOperations


class LittleAlgorithm:
    """Реализация алгоритма Литтла методом ветвей и границ"""

    INF = 999

    def __init__(self, cost_matrix: List[List[int]], verbose: bool = True):
        """
        Инициализация алгоритма

        Args:
            cost_matrix: Исходная матрица затрат
            verbose: Выводить ли промежуточные результаты
        """
        self.original_matrix = copy.deepcopy(cost_matrix)
        self.n = len(cost_matrix)
        self.verbose = verbose
        self.best_tour = None
        self.best_cost = float('inf')
        self.iteration = 0

    def solve(self) -> Tuple[Optional[List[int]], int, List]:
        """
        Решить задачу коммивояжера

        Returns:
            Кортеж (оптимальный маршрут, стоимость, список всех итераций)
        """
        if self.verbose:
            print("=" * 80)
            print("АЛГОРИТМ ЛИТТЛА ДЛЯ РЕШЕНИЯ ЗАДАЧИ КОММИВОЯЖЕРА")
            print("=" * 80)
            print(f"\nИсходная матрица затрат (размер {self.n}×{self.n}):")
            print(MatrixOperations.format_matrix(self.original_matrix))

        # Начальное приведение
        reduced_matrix, reduction_const = MatrixOperations.full_reduction(self.original_matrix)

        if self.verbose:
            print(f"\nНижняя граница (оценка 0): {reduction_const}")

        # Запускаем рекурсивный поиск
        used_edges = []
        used_rows = set()
        used_cols = set()

        self._branch_and_bound(
            reduced_matrix,
            reduction_const,
            used_edges,
            used_rows,
            used_cols,
            level=0
        )

        if self.verbose:
            print("\n" + "=" * 80)
            print("РЕШЕНИЕ НАЙДЕНО")
            print("=" * 80)

            if self.best_tour:
                tour_str = ' → '.join([str(x+1) for x in self.best_tour]) + f" → {self.best_tour[0]+1}"
                print(f"\nОптимальный маршрут: {tour_str}")
                print(f"Минимальная стоимость: {self.best_cost}")
            else:
                print("\nРешение не найдено")

        return self.best_tour, self.best_cost, []

    def _branch_and_bound(self, matrix: List[List[int]], bound: int,
                         used_edges: List[Tuple[int, int]],
                         used_rows: Set[int], used_cols: Set[int],
                         level: int):
        """
        Рекурсивный поиск методом ветвей и границ
        """
        self.iteration += 1

        # Отсечение
        if bound >= self.best_cost:
            if self.verbose and level < 3:
                print(f"\n{'─' * 80}")
                print(f"ИТЕРАЦИЯ {self.iteration}: Отсечение (граница {bound} >= {self.best_cost})")
            return

        # Если все города использованы
        if len(used_edges) == self.n:
            # Замыкаем тур
            cost = self.original_matrix[used_edges[-1][1]][used_edges[0][0]]
            if cost != self.INF:
                final_cost = bound + cost
                if final_cost < self.best_cost:
                    self.best_cost = final_cost
                    self.best_tour = self._build_tour_from_edges(used_edges)
                    if self.verbose:
                        print(f"\n{'═' * 80}")
                        print(f"НАЙДЕН ПОЛНЫЙ МАРШРУТ")
                        print(f"{'═' * 80}")
                        if self.best_tour:
                            tour_str = ' → '.join([str(x+1) for x in self.best_tour]) + f" → {self.best_tour[0]+1}"
                            print(f"Маршрут: {tour_str}")
                            print(f"Стоимость: {final_cost}")
            return

        if self.verbose:
            print(f"\n{'─' * 80}")
            print(f"ИТЕРАЦИЯ {self.iteration} (уровень {level})")
            print(f"{'─' * 80}")
            print(f"Нижняя граница: {bound}")
            print(f"Построенные рёбра: {[(x[0]+1, x[1]+1) for x in used_edges]}")

            # Выводим текущую матрицу
            # Блокируем уже использованные строки/столбцы
            display_matrix = copy.deepcopy(matrix)
            for i in used_rows:
                for j in range(len(display_matrix[0])):
                    display_matrix[i][j] = self.INF
            for j in used_cols:
                for i in range(len(display_matrix)):
                    display_matrix[i][j] = self.INF

            print(f"\nМатрица ({len(matrix)}×{len(matrix)}):")
            print(MatrixOperations.format_matrix(display_matrix))

        # Вычисляем штрафы
        penalties = {}
        for i in range(len(matrix)):
            if i in used_rows:
                continue
            for j in range(len(matrix[0])):
                if j in used_cols:
                    continue
                if matrix[i][j] == 0:
                    # Найти минимум в строке
                    row_min = float('inf')
                    for k in range(len(matrix[0])):
                        if k != j and k not in used_cols and matrix[i][k] != self.INF:
                            row_min = min(row_min, matrix[i][k])

                    # Найти минимум в столбце
                    col_min = float('inf')
                    for k in range(len(matrix)):
                        if k != i and k not in used_rows and matrix[k][j] != self.INF:
                            col_min = min(col_min, matrix[k][j])

                    penalty = 0
                    if row_min != float('inf'):
                        penalty += row_min
                    if col_min != float('inf'):
                        penalty += col_min

                    penalties[(i, j)] = penalty

        if not penalties:
            if self.verbose and level < 3:
                print("Нет доступных рёбер - задача неразрешима")
            return

        # Находим ребро с максимальным штрафом
        best_edge = max(penalties.items(), key=lambda x: x[1])
        edge_pos = best_edge[0]
        penalty = best_edge[1]

        if self.verbose and level < 3:
            print(f"\nТоп штрафы:")
            for edge, pen in sorted(penalties.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  ({edge[0]+1}, {edge[1]+1}): {pen}")
            print(f"\nВыбранное ребро: ({edge_pos[0]+1}, {edge_pos[1]+1}) со штрафом {penalty}")

        # ВАРИАНТ 1: Включить ребро
        if self.verbose and level < 3:
            print(f"\n┌─ ВАРИАНТ 1: Включить ребро ({edge_pos[0]+1}, {edge_pos[1]+1})")

        new_edges_1 = used_edges + [edge_pos]
        new_rows_1 = used_rows.copy()
        new_cols_1 = used_cols.copy()

        # Блокируем обратное ребро
        new_matrix_1 = copy.deepcopy(matrix)
        new_matrix_1[edge_pos[1]][edge_pos[0]] = self.INF

        # Отмечаем строку и столбец как использованные
        new_rows_1.add(edge_pos[0])
        new_cols_1.add(edge_pos[1])

        # Приводим новую матрицу
        reduced_1, reduction_1 = self._reduce_matrix(new_matrix_1, new_rows_1, new_cols_1)
        new_bound_1 = bound + reduction_1

        if self.verbose and level < 3:
            print(f"    Новая граница: {new_bound_1}")

        self._branch_and_bound(
            new_matrix_1,
            new_bound_1,
            new_edges_1,
            new_rows_1,
            new_cols_1,
            level + 1
        )

        # ВАРИАНТ 2: Исключить ребро
        if self.verbose and level < 3:
            print(f"\n└─ ВАРИАНТ 2: Исключить ребро ({edge_pos[0]+1}, {edge_pos[1]+1})")

        new_matrix_2 = copy.deepcopy(matrix)
        new_matrix_2[edge_pos[0]][edge_pos[1]] = self.INF

        # Приводим матрицу
        reduced_2, reduction_2 = self._reduce_matrix(new_matrix_2, used_rows, used_cols)
        new_bound_2 = bound + reduction_2

        if self.verbose and level < 3:
            print(f"    Новая граница: {new_bound_2}")

        self._branch_and_bound(
            new_matrix_2,
            new_bound_2,
            used_edges,
            used_rows,
            used_cols,
            level + 1
        )

    def _reduce_matrix(self, matrix: List[List[int]],
                      used_rows: Set[int], used_cols: Set[int]) -> Tuple[List[List[int]], int]:
        """
        Привести матрицу, исключая использованные строки/столбцы

        Returns:
            Кортеж (матрица, константа приведения)
        """
        total_reduction = 0

        # Приведение строк
        for i in range(len(matrix)):
            if i in used_rows:
                continue

            row_min = float('inf')
            for j in range(len(matrix[0])):
                if j not in used_cols and matrix[i][j] != self.INF:
                    row_min = min(row_min, matrix[i][j])

            if row_min != 0 and row_min != float('inf'):
                total_reduction += row_min
                for j in range(len(matrix[0])):
                    if j not in used_cols and matrix[i][j] != self.INF:
                        matrix[i][j] -= row_min

        # Приведение столбцов
        for j in range(len(matrix[0])):
            if j in used_cols:
                continue

            col_min = float('inf')
            for i in range(len(matrix)):
                if i not in used_rows and matrix[i][j] != self.INF:
                    col_min = min(col_min, matrix[i][j])

            if col_min != 0 and col_min != float('inf'):
                total_reduction += col_min
                for i in range(len(matrix)):
                    if i not in used_rows and matrix[i][j] != self.INF:
                        matrix[i][j] -= col_min

        return matrix, total_reduction

    def _build_tour_from_edges(self, edges: List[Tuple[int, int]]) -> Optional[List[int]]:
        """
        Построить маршрут из набора рёбер

        Args:
            edges: Список рёбер (i,j)

        Returns:
            Маршрут в виде списка городов
        """
        if len(edges) != self.n:
            return None

        # Построить граф
        graph = {}
        for i, j in edges:
            if i in graph:
                return None  # Ошибка: два ребра из одного города
            graph[i] = j

        # Пройти по графу
        tour = []
        current = 0
        visited = set()

        for _ in range(self.n):
            if current in visited:
                break  # Циклы сомкнулись раньше

            tour.append(current)
            visited.add(current)
            current = graph.get(current)
            if current is None:
                break

        return tour if len(tour) == self.n else None
