import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from copy import deepcopy

@dataclass
class SimplexIteration:
    """Данные одной итерации симплекс-метода"""
    iteration: int
    tableau: np.ndarray  # Симплекс-таблица
    basis: List[int]  # Индексы базисных переменных
    basis_names: List[str]  # Имена базисных переменных
    c_basis: np.ndarray  # Коэффициенты целевой функции для базисных переменных
    x_basis: np.ndarray  # Значения базисных переменных
    objective_value: float  # Значение целевой функции
    reduced_costs: np.ndarray  # Приведённые стоимости
    entering_var_idx: Optional[int]  # Индекс входящей переменной
    entering_var_name: Optional[str]  # Имя входящей переменной
    leaving_var_idx: Optional[int]  # Индекс выходящей переменной
    leaving_var_name: Optional[str]  # Имя выходящей переменной
    is_optimal: bool  # Оптимальное ли решение

class SimplexTableauSolver:
    """Решатель ЗЛП табличным симплекс-методом"""

    def __init__(self, c, A_ub, b_ub, A_eq=None, b_eq=None, maximize=True,
                 variable_names=None, constraint_names=None, verbose=True):
        """
        Инициализация решателя

        Args:
            c: Коэффициенты целевой функции
            A_ub: Матрица коэффициентов для ≤ ограничений
            b_ub: Правая часть для ≤ ограничений
            A_eq: Матрица коэффициентов для = ограничений
            b_eq: Правая часть для = ограничений
            maximize: True для максимизации, False для минимизации
            variable_names: Имена переменных
            constraint_names: Имена ограничений
            verbose: Выводить ли детали
        """
        self.c = np.array(c, dtype=float)
        self.A_ub = np.array(A_ub, dtype=float) if A_ub is not None else np.empty((0, len(c)))
        self.b_ub = np.array(b_ub, dtype=float) if b_ub is not None else np.array([])
        self.A_eq = np.array(A_eq, dtype=float) if A_eq is not None else np.empty((0, len(c)))
        self.b_eq = np.array(b_eq, dtype=float) if b_eq is not None else np.array([])

        self.maximize = maximize
        self.verbose = verbose
        self.n_original = len(c)

        # Имена переменных
        if variable_names is None:
            self.var_names = [f'x{i+1}' for i in range(self.n_original)]
        else:
            self.var_names = variable_names

        # Имена ограничений
        if constraint_names is None:
            n_constraints = len(b_ub) + (len(b_eq) if b_eq is not None else 0)
            self.constraint_names = [f'огр{i+1}' for i in range(n_constraints)]
        else:
            self.constraint_names = constraint_names

        # История итераций
        self.iterations: List[SimplexIteration] = []
        self.optimal_solution = None
        self.optimal_value = None

        # Подготовить стандартную форму
        self._prepare_standard_form()

    def _prepare_standard_form(self):
        """Преобразовать в стандартную форму"""
        # Все ограничения должны быть равенства с неотрицательной правой частью

        # Если нет ограничений ≤, использовать только =
        if (self.A_ub is None or len(self.A_ub) == 0) and self.A_eq is not None:
            self.A = self.A_eq
            self.b = self.b_eq
            self.n_slack = 0
            self.n_artificial = len(self.b_eq)
        else:
            # Добавить slack переменные для ≤ ограничений
            m_ub = len(self.A_ub) if self.A_ub is not None else 0
            m_eq = len(self.A_eq) if self.A_eq is not None and len(self.A_eq) > 0 else 0

            # Сформировать расширенную матрицу с slack переменными
            if m_eq > 0:
                # Есть оба типа ограничений
                slack_matrix = np.eye(m_ub, dtype=float)
                self.A = np.vstack([self.A_ub, self.A_eq])
                self.A = np.hstack([self.A, np.vstack([slack_matrix, np.zeros((m_eq, m_ub))])])
                self.b = np.hstack([self.b_ub, self.b_eq])
            else:
                # Только ≤ ограничения
                self.A = np.hstack([self.A_ub, np.eye(m_ub, dtype=float)])
                self.b = self.b_ub

            self.n_slack = m_ub
            self.n_artificial = m_eq

        # Проверить положительность правой части
        for i, val in enumerate(self.b):
            if val < 0:
                self.A[i] *= -1
                self.b[i] *= -1

        self.m = len(self.b)  # Количество ограничений
        self.n_total = len(self.A[0]) if len(self.A) > 0 else self.n_original  # Всего переменных

    def solve(self) -> Tuple[np.ndarray, float, bool]:
        """
        Решить задачу табличным симплекс-методом

        Returns:
            (x_optimal, objective_value, is_feasible)
        """
        # Инициализировать симплекс-таблицу
        self._initialize_tableau()

        # Итерировать до оптимальности
        iteration = 0
        max_iterations = 1000

        while iteration < max_iterations:
            # Проверить оптимальность
            reduced_costs = self.tableau[0, :-1]

            is_optimal = True
            if self.maximize:
                # Для максимизации: все приведённые стоимости должны быть ≥ 0
                is_optimal = np.all(reduced_costs >= -1e-10)
                if not is_optimal:
                    entering_idx = np.argmin(reduced_costs)
                else:
                    entering_idx = -1
            else:
                # Для минимизации: все приведённые стоимости должны быть ≥ 0
                # (так как мы максимизируем -F, приведённые стоимости = c_j, где положительные - кандидаты для входа)
                is_optimal = np.all(reduced_costs >= -1e-10)
                if not is_optimal:
                    entering_idx = np.argmin(reduced_costs)
                else:
                    entering_idx = -1

            # Сохранить итерацию
            self._save_iteration(iteration, entering_idx, is_optimal)

            if is_optimal:
                break

            # Найти выходящую переменную (минимальное отношение)
            leaving_idx = self._find_leaving_variable(entering_idx)

            if leaving_idx == -1:
                # Задача неограничена
                if self.verbose:
                    print("Задача неограничена!")
                return None, None, False

            # Выполнить pivot операцию
            self._pivot(entering_idx, leaving_idx)

            iteration += 1

        # Извлечь оптимальное решение
        return self._extract_solution()

    def _initialize_tableau(self):
        """Инициализировать симплекс-таблицу"""
        # Преобразуем минимизацию в максимизацию: min(c·x) = -max(-c·x)
        # Строка целевой функции: [коэффициенты целевой | 0]
        # Строки ограничений: [A | b]

        n_vars = self.n_original + self.n_slack + self.n_artificial

        # Целевая функция
        c_row = np.zeros(n_vars + 1)
        # Всегда работаем с коэффициентами для максимизации
        # Если минимизируем, инвертируем: min(F) = max(-F)
        c_coefficients = -self.c if not self.maximize else self.c
        c_row[:self.n_original] = c_coefficients

        # Комбинировать целевую функцию и ограничения
        A_augmented = np.hstack([self.A, self.b.reshape(-1, 1)])
        self.tableau = np.vstack([c_row, A_augmented])

        # Инициальный базис: slack переменные
        self.basis = list(range(self.n_original, self.n_original + self.n_slack))

    def _save_iteration(self, iteration: int, entering_idx: int, is_optimal: bool):
        """Сохранить данные итерации"""
        # Извлечь базисные значения
        x_basis = np.zeros(self.m)
        for i, basis_idx in enumerate(self.basis):
            x_basis[i] = self.tableau[i+1, -1]

        # Приведённые стоимости (первая строка таблицы)
        reduced_costs = self.tableau[0, :-1].copy()

        # Имена переменных
        var_names = self.var_names + [f's{i+1}' for i in range(self.n_slack)]
        basis_names = [var_names[idx] for idx in self.basis]

        # Коэффициенты целевой функции для базисных
        c_basis = np.array([self.c[idx] if idx < self.n_original else 0 for idx in self.basis])

        entering_name = var_names[entering_idx] if entering_idx >= 0 else None

        iteration_data = SimplexIteration(
            iteration=iteration,
            tableau=self.tableau.copy(),
            basis=self.basis.copy(),
            basis_names=basis_names,
            c_basis=c_basis,
            x_basis=x_basis,
            objective_value=self.tableau[0, -1],
            reduced_costs=reduced_costs,
            entering_var_idx=entering_idx,
            entering_var_name=entering_name,
            leaving_var_idx=None,
            leaving_var_name=None,
            is_optimal=is_optimal
        )

        self.iterations.append(iteration_data)

    def _find_leaving_variable(self, entering_idx: int) -> int:
        """
        Найти выходящую переменную (правило минимального отношения)

        Args:
            entering_idx: Индекс входящей переменной

        Returns:
            Индекс выходящей базисной переменной (или -1 если неограничена)
        """
        # Столбец входящей переменной
        col = self.tableau[1:, entering_idx]

        # Правая часть
        rhs = self.tableau[1:, -1]

        # Найти положительные элементы столбца
        min_ratio = np.inf
        leaving_row = -1

        for i in range(len(col)):
            if col[i] > 1e-10:
                ratio = rhs[i] / col[i]
                if ratio < min_ratio:
                    min_ratio = ratio
                    leaving_row = i

        return leaving_row if leaving_row >= 0 else -1

    def _pivot(self, entering_col: int, leaving_row: int):
        """
        Выполнить pivot операцию

        Args:
            entering_col: Индекс столбца входящей переменной
            leaving_row: Индекс строки выходящей переменной (0-indexed от ограничений)
        """
        # Корректировка на строку целевой функции
        leaving_row += 1

        # Получить pivot элемент
        pivot = self.tableau[leaving_row, entering_col]

        # Нормализовать строку pivot
        self.tableau[leaving_row] /= pivot

        # Исключить другие элементы в столбце
        for i in range(len(self.tableau)):
            if i != leaving_row:
                multiplier = self.tableau[i, entering_col]
                self.tableau[i] -= multiplier * self.tableau[leaving_row]

        # Обновить базис
        old_basis_idx = self.basis[leaving_row - 1]
        self.basis[leaving_row - 1] = entering_col

    def _extract_solution(self) -> Tuple[np.ndarray, float, bool]:
        """Извлечь оптимальное решение"""
        x_optimal = np.zeros(self.n_original)

        for i, basis_idx in enumerate(self.basis):
            if basis_idx < self.n_original:
                x_optimal[basis_idx] = self.tableau[i+1, -1]

        # Значение из таблицы (это максимизация -F для минимизации, или максимизация F для максимизации)
        # Чтобы получить исходное значение:
        # - Для максимизации: берём tableau[0,-1] с отрицательным знаком
        # - Для минимизации: берём tableau[0,-1] с положительным знаком (так как там -F)
        objective_value = -self.tableau[0, -1]

        self.optimal_solution = x_optimal
        self.optimal_value = objective_value

        return x_optimal, objective_value, True

    def print_solution(self):
        """Вывести решение"""
        print("\n" + "="*70)
        print("ОПТИМАЛЬНОЕ РЕШЕНИЕ")
        print("="*70)

        if self.optimal_solution is None:
            print("Решение не найдено")
            return

        print("\nОптимальные значения переменных:")
        for i, name in enumerate(self.var_names):
            print(f"  {name} = {self.optimal_solution[i]:.4f}")

        print(f"\nЗначение целевой функции: {self.optimal_value:.4f}")

    def print_iterations(self):
        """Вывести все итерации"""
        print("\n" + "="*70)
        print("ИТЕРАЦИИ СИМПЛЕКС-МЕТОДА")
        print("="*70)

        for iter_data in self.iterations:
            print(f"\n{'='*70}")
            print(f"Итерация {iter_data.iteration}")
            print(f"{'='*70}")

            print(f"\nБазис: {', '.join(iter_data.basis_names)}")
            print(f"Значение целевой функции: {iter_data.objective_value:.4f}")

            print("\nТекущие значения переменных:")
            var_names = self.var_names + [f's{i+1}' for i in range(self.n_slack)]
            for i, name in enumerate(var_names):
                if i < len(iter_data.reduced_costs):
                    if i in iter_data.basis:
                        idx = iter_data.basis.index(i)
                        print(f"  {name} = {iter_data.x_basis[idx]:.4f}")
                    else:
                        print(f"  {name} = 0.0000 (приведённая стоимость: {iter_data.reduced_costs[i]:.4f})")

            if iter_data.is_optimal:
                print("\n*** ОПТИМАЛЬНОЕ РЕШЕНИЕ НАЙДЕНО ***")
            else:
                print(f"\nВходящая переменная: {iter_data.entering_var_name}")

            # Вывести таблицу
            self._print_tableau(iter_data.tableau)

    def _print_tableau(self, tableau: np.ndarray):
        """Вывести симплекс-таблицу"""
        print("\nСимплекс-таблица:")

        var_names = self.var_names + [f's{i+1}' for i in range(self.n_slack)]

        # Заголовок
        header = "   " + " ".join(f"{name:>10}" for name in var_names) + f"  {'RHS':>12}"
        print(header)
        print("-" * len(header))

        # Строка целевой функции
        row_data = [f"{tableau[0, i]:>10.4f}" for i in range(len(var_names))]
        print("Z: " + " ".join(row_data) + f"  {tableau[0, -1]:>12.4f}")

        # Строки ограничений
        for i in range(1, len(tableau)):
            row_data = [f"{tableau[i, j]:>10.4f}" for j in range(len(var_names))]
            print(f"R{i}: " + " ".join(row_data) + f"  {tableau[i, -1]:>12.4f}")
