import numpy as np
from itertools import combinations
from typing import Tuple, Optional


class SimpleLinearSolver:
    """Простой решатель ЛП перебором базисов"""

    def __init__(self, c, A_ub, b_ub, variable_names=None, verbose=False):
        self.c_original = np.array(c, dtype=float)
        self.A_ub = np.array(A_ub, dtype=float)
        self.b_ub = np.array(b_ub, dtype=float)
        self.variable_names = variable_names or [f'x{i+1}' for i in range(len(c))]
        self.verbose = verbose
        self.m = len(self.A_ub)  # Количество ограничений
        self.n_original = len(self.c_original)  # Количество исходных переменных

        # Добавляем slack переменные
        self.n = self.n_original + self.m
        self.c = np.hstack([self.c_original, np.zeros(self.m)])

        # Расширяем матрицу ограничений со slack переменными
        slack_matrix = np.eye(self.m)
        self.A = np.hstack([self.A_ub, slack_matrix])

    def solve(self) -> Tuple[Optional[np.ndarray], Optional[float], bool]:
        """
        Решить ЛП перебором базисов

        Returns:
            (x_optimal, objective_value, is_feasible)
        """
        best_solution = None
        best_value = float('inf')
        best_basis = None

        # Перебираем все возможные базисы (комбинации m переменных из n)
        for basis_indices in combinations(range(self.n), self.m):
            # Проверяем, может ли это быть базисом
            A_basis = self.A[:, list(basis_indices)]

            # Пробуем решить систему
            try:
                det = np.linalg.det(A_basis)
                if abs(det) < 1e-10:  # Вырожденный базис
                    continue

                # Решаем: A_basis * x_basis = b
                x_basis = np.linalg.solve(A_basis, self.b_ub)

                # Проверяем неотрицательность базисных переменных
                if not np.all(x_basis >= -1e-6):
                    continue

                # Восстанавливаем полное решение
                x_full = np.zeros(self.n)
                for i, idx in enumerate(basis_indices):
                    x_full[idx] = x_basis[i]

                # Проверяем неотрицательность всех переменных
                if not np.all(x_full >= -1e-6):
                    continue

                # Проверяем ограничения: Ax = b
                check = self.A @ x_full
                if not np.allclose(check, self.b_ub, atol=1e-6):
                    continue

                # Берем только исходные переменные
                x_original = x_full[:self.n_original]

                # Вычисляем целевую функцию (только по исходным переменным)
                obj_value = np.dot(self.c_original, x_original)

                if obj_value < best_value:
                    best_value = obj_value
                    best_solution = x_original
                    best_basis = basis_indices

            except (np.linalg.LinAlgError, np.OverflowError):
                continue

        if best_solution is not None:
            return best_solution, best_value, True
        else:
            return None, None, False

    def print_solution(self, x_solution, obj_value):
        """Вывести решение"""
        print("\n" + "="*70)
        print("ОПТИМАЛЬНОЕ РЕШЕНИЕ")
        print("="*70)

        print("\nОптимальные значения переменных:")
        for name, val in zip(self.variable_names, x_solution):
            if val > 1e-6:
                print(f"  {name} = {val:,.4f}")
            else:
                print(f"  {name} = 0.0000")

        print(f"\nЗначение целевой функции: {obj_value:,.2f}")

    def print_problem(self):
        """Вывести информацию о задаче"""
        print("\n" + "="*70)
        print("СВЕДЕНИЯ О ЗАДАЧЕ")
        print("="*70)
        print(f"Количество переменных: {self.n}")
        print(f"Количество ограничений: {self.m}")
        print(f"Тип: Минимизация")
        print(f"\nЦелевая функция: F = {' + '.join([f'{c:.0f}·{name}' for c, name in zip(self.c, self.variable_names)])}")


class SimplexTableMethod:
    """Таблич ный симплекс-метод"""

    def __init__(self, c, A_eq, b_eq, variable_names=None, verbose=False):
        """
        Решать задачу в стандартной форме: min c'x, s.t. Ax=b, x>=0

        Args:
            c: Коэффициенты целевой функции
            A_eq: Матрица ограничений (все равенства)
            b_eq: Правая часть
            variable_names: Имена переменных
            verbose: Выводить ли детали
        """
        self.c = np.array(c, dtype=float)
        self.A = np.array(A_eq, dtype=float)
        self.b = np.array(b_eq, dtype=float)
        self.variable_names = variable_names or [f'x{i+1}' for i in range(len(c))]
        self.verbose = verbose
        self.m = len(self.A)  # Ограничения
        self.n = len(self.c)  # Переменные
        self.iterations = []

    def solve(self) -> Tuple[Optional[np.ndarray], Optional[float], bool]:
        """Решить"""
        # Инициализировать таблицу
        self._init_tableau()

        iteration = 0
        max_iterations = 1000

        while iteration < max_iterations:
            # Проверить оптимальность
            reduced_costs = self.tableau[0, :-1]

            # Для минимизации: все приведённые стоимости должны быть >= 0
            if np.all(reduced_costs >= -1e-10):
                break

            # Выбрать входящую переменную (минимальная приведённая стоимость)
            entering_idx = np.argmin(reduced_costs)

            # Найти выходящую переменную
            col = self.tableau[1:, entering_idx]
            rhs = self.tableau[1:, -1]

            min_ratio = np.inf
            leaving_row = -1

            for i in range(len(col)):
                if col[i] > 1e-10:
                    ratio = rhs[i] / col[i]
                    if ratio < min_ratio:
                        min_ratio = ratio
                        leaving_row = i

            if leaving_row == -1:
                # Unbounded
                return None, None, False

            # Pivot
            pivot_row = leaving_row + 1
            pivot_val = self.tableau[pivot_row, entering_idx]
            self.tableau[pivot_row] /= pivot_val

            for i in range(len(self.tableau)):
                if i != pivot_row:
                    mult = self.tableau[i, entering_idx]
                    self.tableau[i] -= mult * self.tableau[pivot_row]

            iteration += 1

        # Извлечь решение
        x_solution = np.zeros(self.n)
        for i in range(self.m):
            # Найти какая переменная соответствует i-й строке
            row = self.tableau[i+1, :-1]
            if np.count_nonzero(row) == 1:
                idx = np.where(row != 0)[0][0]
                if idx < self.n:
                    x_solution[idx] = self.tableau[i+1, -1]

        obj_value = -self.tableau[0, -1]
        return x_solution, obj_value, True

    def _init_tableau(self):
        """Инициализировать таблицу"""
        self.tableau = np.zeros((self.m + 1, self.n + 1))
        self.tableau[0, :self.n] = -self.c  # Для минимизации
        self.tableau[1:, :self.n] = self.A
        self.tableau[1:, self.n] = self.b
