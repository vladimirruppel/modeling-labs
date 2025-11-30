#!/usr/bin/env python3
"""
ЛР 4: Решение транспортной задачи
Вариант 18 - Грузовые автомобили

Методы:
1. Метод северо-западного угла (для получения начального плана)
2. Метод наименьшей стоимости (альтернативный начальный план)
3. Метод потенциалов (для улучшения решения)
"""

import os
import sys
from utils import read_data, save_results, print_problem_info
from transport_solver import TransportProblem


def main():
    print("\n" + "="*70)
    print("ЛР 4: РЕШЕНИЕ ТРАНСПОРТНОЙ ЗАДАЧИ")
    print("Вариант 18 - Грузовые автомобили")
    print("="*70)

    # Путь к файлу с данными
    data_file = "data/variant_18.txt"

    # Проверяем наличие файла
    if not os.path.exists(data_file):
        print(f"\n✗ Файл {data_file} не найден!")
        return

    # Читаем данные
    print(f"\n→ Читаем данные из {data_file}...")
    supplies, demands, costs = read_data(data_file)

    # Выводим информацию о задаче
    print_problem_info(supplies, demands, costs)

    # Создаем объект задачи
    problem = TransportProblem(supplies, demands, costs)

    # Меню
    while True:
        print("\n" + "="*70)
        print("МЕНЮ")
        print("="*70)
        print("1. Решить методом северо-западного угла + потенциалы")
        print("2. Решить методом наименьшей стоимости + потенциалы")
        print("3. Просмотреть исходные данные")
        print("4. Выход")
        print("="*70)

        choice = input("\nВыберите пункт (1-4): ").strip()

        if choice == "1":
            print("\n" + "="*70)
            print("РЕШЕНИЕ МЕТОДОМ СЕВЕРО-ЗАПАДНОГО УГЛА")
            print("="*70)

            # Получаем начальный план
            problem.northwest_corner_method()

            # Улучшаем методом потенциалов
            problem.potential_method()

            # Сохраняем результаты
            save_results("output/solution_nwc.txt", problem, "Северо-западный угол")
            print("\n✓ Результаты сохранены в output/solution_nwc.txt")

        elif choice == "2":
            print("\n" + "="*70)
            print("РЕШЕНИЕ МЕТОДОМ НАИМЕНЬШЕЙ СТОИМОСТИ")
            print("="*70)

            # Получаем начальный план
            problem.minimum_cost_method()

            # Улучшаем методом потенциалов
            problem.potential_method()

            # Сохраняем результаты
            save_results("output/solution_mc.txt", problem, "Наименьшая стоимость")
            print("\n✓ Результаты сохранены в output/solution_mc.txt")

        elif choice == "3":
            print_problem_info(supplies, demands, costs)

        elif choice == "4":
            print("\nДо свидания!")
            break

        else:
            print("\n✗ Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()
