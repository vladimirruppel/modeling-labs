#!/usr/bin/env python3
"""
Программа решения задачи коммивояжера методом Литтла
Лабораторная работа №5 - Задача о переналадке оборудования
"""
import os
import sys
import time
from typing import List, Optional
from pathlib import Path

# Добавляем директорию в путь для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from matrix_utils import MatrixOperations
from little_algorithm import LittleAlgorithm
from output_formatter import OutputFormatter
from tree_builder import BranchingTree


class TSPSolver:
    """Главный класс программы решения задачи коммивояжера"""

    def __init__(self):
        """Инициализация программы"""
        self.formatter = OutputFormatter()
        self.current_matrix = None
        self.current_tour = None
        self.current_cost = None

    def load_matrix_from_file(self, filepath: str) -> Optional[List[List[int]]]:
        """
        Загрузить матрицу из файла

        Args:
            filepath: Путь к файлу

        Returns:
            Матрица или None если ошибка
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Первая строка - размер матрицы
            n = int(lines[0].strip())

            matrix = []
            for i in range(1, n + 1):
                if i >= len(lines):
                    self.formatter.print_error(f"Недостаточно строк в файле (ожидается {n})")
                    return None

                values = [int(x) for x in lines[i].strip().split()]
                if len(values) != n:
                    self.formatter.print_error(f"Ошибка в строке {i}: ожидается {n} значений")
                    return None

                matrix.append(values)

            return matrix

        except FileNotFoundError:
            self.formatter.print_error(f"Файл не найден: {filepath}")
            return None
        except ValueError as e:
            self.formatter.print_error(f"Ошибка при чтении данных: {e}")
            return None

    def solve_tsp(self, matrix: List[List[int]], verbose: bool = True) -> bool:
        """
        Решить задачу коммивояжера

        Args:
            matrix: Матрица затрат
            verbose: Выводить ли промежуточные результаты

        Returns:
            True если успешно, False иначе
        """
        try:
            self.current_matrix = matrix

            # Решение
            start_time = time.time()
            algorithm = LittleAlgorithm(matrix, verbose=verbose)
            self.current_tour, self.current_cost, states = algorithm.solve()
            elapsed_time = time.time() - start_time

            if not self.current_tour:
                self.formatter.print_error("Не удалось найти решение")
                return False

            # Вычисление стоимостей переходов
            costs = []
            for i in range(len(self.current_tour)):
                from_city = self.current_tour[i]
                to_city = self.current_tour[(i + 1) % len(self.current_tour)]
                cost = matrix[from_city][to_city]
                costs.append(cost)

            print(f"\n\n{'=' * 80}")
            print("ИТОГОВЫЙ РЕЗУЛЬТАТ")
            print(f"{'=' * 80}")

            tour_str = ' → '.join([str(x+1) for x in self.current_tour]) + f" → {self.current_tour[0]+1}"
            print(f"\nОптимальный маршрут: {tour_str}")
            print(f"Минимальная стоимость: {self.current_cost}")
            print(f"Время выполнения: {elapsed_time:.4f} сек")

            print(self.formatter.format_tour_table(self.current_tour, costs))

            # Сохранение результатов
            self.formatter.save_solution(self.current_tour, self.current_cost, len(matrix))
            self.formatter.print_success("Результаты сохранены в директорию output/")

            return True

        except Exception as e:
            self.formatter.print_error(f"Ошибка при решении: {e}")
            import traceback
            traceback.print_exc()
            return False

    def show_menu(self):
        """Показать меню программы"""
        self.formatter.print_header()
        self.formatter.print_menu()

    def task_1_variant_18(self):
        """Решить задачу для варианта 18"""
        print("РЕШЕНИЕ ДЛЯ ВАРИАНТА 18 (матрица 6×6)")
        print("-" * 80)

        # Определяем путь к файлу данных
        data_file = os.path.join(
            os.path.dirname(__file__),
            "data",
            "variant_18.txt"
        )

        if not os.path.exists(data_file):
            self.formatter.print_error(f"Файл не найден: {data_file}")
            return

        print(f"Загрузка данных из: {data_file}")
        matrix = self.load_matrix_from_file(data_file)

        if matrix is None:
            return

        print(f"Матрица загружена успешно ({len(matrix)}×{len(matrix)})\n")

        if self.solve_tsp(matrix, verbose=True):
            self.formatter.print_success("Задача решена")

    def task_2_custom_file(self):
        """Решить задачу для пользовательского файла"""
        print("\nВВОД ПУТИ К ФАЙЛУ С МАТРИЦЕЙ")
        print("-" * 80)
        print("Формат файла:")
        print("  Строка 1: Размер матрицы (n)")
        print("  Строки 2-n+1: Строки матрицы (n значений в каждой)")
        print("  Пример:")
        print("    6")
        print("    999 28 2 20 23 12")
        print("    17 999 25 27 21 23")
        print("    ...")

        filepath = input("\nВведите путь к файлу: ").strip()

        if not filepath:
            print("Отменено")
            return

        # Расширяем путь если нужно
        if not os.path.isabs(filepath):
            filepath = os.path.join(os.getcwd(), filepath)

        matrix = self.load_matrix_from_file(filepath)
        if matrix is None:
            return

        print(f"\nМатрица загружена успешно ({len(matrix)}×{len(matrix)})")
        print("\nПолный вывод алгоритма? (y/n): ", end="")
        verbose = input().strip().lower() != 'n'

        if self.solve_tsp(matrix, verbose=verbose):
            self.formatter.print_success("Задача решена")

    def task_3_lecture_example(self):
        """Тестовый пример из лекции (4×4)"""
        print("\nТЕСТОВЫЙ ПРИМЕР ИЗ ЛЕКЦИИ (матрица 4×4)")
        print("-" * 80)

        # Пример из лекции
        matrix = [
            [999, 29, 31, 45],
            [23, 999, 35, 15],
            [27, 33, 999, 18],
            [29, 25, 17, 999]
        ]

        print("Матрица затрат:")
        print(MatrixOperations.format_matrix(matrix))

        print("\nПолный вывод алгоритма? (y/n): ", end="")
        verbose = input().strip().lower() != 'n'

        if self.solve_tsp(matrix, verbose=verbose):
            self.formatter.print_success("Задача решена")

    def run(self):
        """Главный цикл программы"""
        while True:
            self.show_menu()

            choice = input("Выберите задачу (1-4): ").strip()

            if choice == "1":
                self.task_1_variant_18()
                input("\nНажмите Enter для продолжения...")

            elif choice == "2":
                self.task_2_custom_file()
                input("\nНажмите Enter для продолжения...")

            elif choice == "3":
                self.task_3_lecture_example()
                input("\nНажмите Enter для продолжения...")

            elif choice == "4":
                print("До свидания!")
                break

            else:
                print("Неверный выбор. Попробуйте снова.")
                input("\nНажмите Enter для продолжения...")


def main():
    """Точка входа"""
    solver = TSPSolver()
    solver.run()


if __name__ == "__main__":
    main()
