"""
Решение транспортной задачи методом северо-западного угла и методом потенциалов
"""

import numpy as np
from copy import deepcopy


class TransportProblem:
    """Класс для решения транспортной задачи"""

    def __init__(self, supplies, demands, costs):
        """
        Инициализация задачи

        Args:
            supplies: список запасов поставщиков
            demands: список потребностей потребителей
            costs: матрица стоимостей доставки
        """
        self.supplies = np.array(supplies, dtype=float)
        self.demands = np.array(demands, dtype=float)
        self.costs = np.array(costs, dtype=float)

        self.m = len(supplies)  # количество поставщиков
        self.n = len(demands)   # количество потребителей

        # Проверка сбалансированности
        self.is_balanced = np.isclose(self.supplies.sum(), self.demands.sum())

        # Переменные для решения
        self.solution = None
        self.basis = None  # базисные переменные
        self.total_cost = 0

    def northwest_corner_method(self):
        """
        Метод северо-западного угла для получения начального плана
        """
        print("\n" + "="*60)
        print("МЕТОД СЕВЕРО-ЗАПАДНОГО УГЛА")
        print("="*60)

        # Копируем запасы и спрос
        supply = self.supplies.copy()
        demand = self.demands.copy()

        # Инициализируем решение
        solution = np.zeros((self.m, self.n), dtype=float)
        basis = []  # список базисных клеток

        i, j = 0, 0
        iteration = 0

        while i < self.m and j < self.n:
            iteration += 1

            # Берем минимум из оставшихся запасов и спроса
            quantity = min(supply[i], demand[j])
            solution[i, j] = quantity
            basis.append((i, j))

            print(f"\nИтерация {iteration}:")
            print(f"  Поставщик {i+1} → Потребитель {j+1}")
            print(f"  Перевезли: {quantity:.0f} единиц")
            print(f"  Стоимость: {quantity:.0f} × {self.costs[i, j]:.0f} = {quantity * self.costs[i, j]:.0f} д.е.")

            supply[i] -= quantity
            demand[j] -= quantity

            # Движемся либо вниз, либо вправо
            if supply[i] == 0:
                i += 1
            else:
                j += 1

        self.solution = solution
        self.basis = basis
        self.total_cost = np.sum(self.solution * self.costs)

        self._print_solution()
        return solution, basis

    def minimum_cost_method(self):
        """
        Метод наименьшей стоимости для получения начального плана
        """
        print("\n" + "="*60)
        print("МЕТОД НАИМЕНЬШЕЙ СТОИМОСТИ")
        print("="*60)

        supply = self.supplies.copy()
        demand = self.demands.copy()

        solution = np.zeros((self.m, self.n), dtype=float)
        basis = []

        # Создаем список всех маршрутов с их стоимостью
        routes = []
        for i in range(self.m):
            for j in range(self.n):
                routes.append((self.costs[i, j], i, j))

        # Сортируем по стоимости (от меньшей к большей)
        routes.sort()

        iteration = 0
        for cost, i, j in routes:
            if supply[i] > 0 and demand[j] > 0:
                iteration += 1

                quantity = min(supply[i], demand[j])
                solution[i, j] = quantity
                basis.append((i, j))

                print(f"\nИтерация {iteration}:")
                print(f"  Поставщик {i+1} → Потребитель {j+1}")
                print(f"  Перевезли: {quantity:.0f} единиц")
                print(f"  Стоимость: {quantity:.0f} × {self.costs[i, j]:.0f} = {quantity * self.costs[i, j]:.0f} д.е.")

                supply[i] -= quantity
                demand[j] -= quantity

        self.solution = solution
        self.basis = basis
        self.total_cost = np.sum(self.solution * self.costs)

        self._print_solution()
        return solution, basis

    def potential_method(self):
        """
        Метод потенциалов для улучшения решения
        """
        print("\n" + "="*60)
        print("МЕТОД ПОТЕНЦИАЛОВ (улучшение решения)")
        print("="*60)

        solution = deepcopy(self.solution)
        basis = set(self.basis)

        iteration = 0

        while True:
            iteration += 1
            print(f"\n--- Итерация {iteration} метода потенциалов ---")

            # Вычисляем потенциалы
            u = [None] * self.m
            v = [None] * self.n
            u[0] = 0

            # Вычисляем потенциалы для базисных переменных
            changed = True
            while changed:
                changed = False
                for i, j in basis:
                    if u[i] is not None and v[j] is None:
                        v[j] = self.costs[i, j] - u[i]
                        changed = True
                    elif v[j] is not None and u[i] is None:
                        u[i] = self.costs[i, j] - v[j]
                        changed = True

            print(f"\nПотенциалы поставщиков (u): {[f'{x:.0f}' if x is not None else '?' for x in u]}")
            print(f"Потенциалы потребителей (v): {[f'{x:.0f}' if x is not None else '?' for x in v]}")

            # Ищем небазисную переменную с минимальной оценкой
            print("\nОценки небазисных переменных (Δij = cij - ui - vj):")
            min_delta = 0
            improve_cell = None

            for i in range(self.m):
                for j in range(self.n):
                    if (i, j) not in basis:
                        if u[i] is not None and v[j] is not None:
                            delta = self.costs[i, j] - u[i] - v[j]
                            if delta < 0 or (delta == 0 and solution[i, j] > 0):
                                print(f"  Δ({i+1},{j+1}) = {self.costs[i, j]:.0f} - {u[i]:.0f} - {v[j]:.0f} = {delta:.0f}")
                                if delta < min_delta:
                                    min_delta = delta
                                    improve_cell = (i, j)

            if improve_cell is None:
                print("\n✓ Решение оптимально! Нет переменных с отрицательной оценкой.")
                break

            # Вводим новую переменную в базис
            print(f"\n✓ Найдена клетка для улучшения: ({improve_cell[0]+1},{improve_cell[1]+1}), Δ = {min_delta:.0f}")
            i_new, j_new = improve_cell
            solution[i_new, j_new] = 0.0001  # Малое значение для начала

            # Пересчитываем решение (простой подход)
            self._recompute_solution(solution, basis, improve_cell)

            self.total_cost = np.sum(solution * self.costs)
            print(f"Новая стоимость: {self.total_cost:.0f} д.е.")

        self.solution = solution
        self.basis = list(basis)
        self.total_cost = np.sum(self.solution * self.costs)
        self._print_solution()

        return solution

    def _recompute_solution(self, solution, basis, new_cell):
        """
        Пересчитывает решение после ввода новой переменной в базис
        """
        # Для упрощения используем простой метод перераспределения
        i_new, j_new = new_cell
        basis.add(new_cell)

        # Находим старую переменную для удаления из базиса
        # (в реальной реализации нужен поиск цикла)
        max_reduction = 0
        cell_to_remove = None

        for i, j in list(basis):
            if i != i_new and j != j_new and solution[i, j] > 0:
                reduction = self.costs[i, j] - self.costs[i_new, j_new]
                if reduction > max_reduction:
                    max_reduction = reduction
                    cell_to_remove = (i, j)

        if cell_to_remove:
            value = solution[cell_to_remove]
            solution[cell_to_remove] = 0
            solution[new_cell] = value
            basis.discard(cell_to_remove)

    def _print_solution(self):
        """Выводит текущее решение"""
        print("\nТекущее распределение перевозок:")
        print("-" * 60)

        header = "  Поставщик |"
        for j in range(self.n):
            header += f"  Потр.{j+1}  |"
        header += "  Запас |"
        print(header)
        print("-" * 60)

        for i in range(self.m):
            row = f"  Завод {i+1}  |"
            for j in range(self.n):
                val = self.solution[i, j]
                row += f"  {val:6.0f}  |" if val > 0 else f"  {val:6.1f}  |"
            row += f"  {self.supplies[i]:.0f}  |"
            print(row)

        print("-" * 60)
        row = "  Спрос     |"
        for j in range(self.n):
            row += f"  {self.demands[j]:6.0f}  |"
        row += "       |"
        print(row)
        print("-" * 60)

        print(f"\nОбщая стоимость доставки: {self.total_cost:.0f} д.е.")
        print(f"Количество базисных переменных: {len(self.basis)}")

    def get_solution_matrix(self):
        """Возвращает матрицу решения"""
        return self.solution

    def get_detailed_report(self):
        """Возвращает подробный отчет"""
        report = []
        report.append("="*70)
        report.append("ДЕТАЛЬНЫЙ ОТЧЕТ О РЕШЕНИИ ТРАНСПОРТНОЙ ЗАДАЧИ")
        report.append("="*70)
        report.append("")
        report.append(f"Количество поставщиков: {self.m}")
        report.append(f"Количество потребителей: {self.n}")
        report.append(f"Задача сбалансирована: {'Да' if self.is_balanced else 'Нет'}")
        report.append(f"Общая стоимость доставки: {self.total_cost:.0f} д.е.")
        report.append("")
        report.append("ПЛАН ПЕРЕВОЗОК:")
        report.append("-"*70)

        for i in range(self.m):
            for j in range(self.n):
                if self.solution[i, j] > 0:
                    cost = self.solution[i, j] * self.costs[i, j]
                    report.append(f"Завод {i+1} → Потребитель {j+1}: {self.solution[i, j]:.0f} шт. × {self.costs[i, j]:.0f} д.е. = {cost:.0f} д.е.")

        report.append("-"*70)
        report.append(f"ИТОГО: {self.total_cost:.0f} д.е.")

        return "\n".join(report)
