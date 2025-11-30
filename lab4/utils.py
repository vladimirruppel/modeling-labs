"""
Утилиты для работы с данными транспортной задачи
"""

import os


def read_data(filepath):
    """
    Читает данные из файла

    Формат файла:
    - Первая строка с запасами поставщиков
    - Вторая строка со спросом потребителей
    - Остальные строки - матрица стоимостей

    Returns:
        tuple: (запасы, спрос, матрица стоимостей)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Пропускаем комментарии
    data_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]

    supplies = list(map(float, data_lines[0].split()))
    demands = list(map(float, data_lines[1].split()))

    costs = []
    for i in range(2, len(data_lines)):
        row = list(map(float, data_lines[i].split()))
        costs.append(row)

    return supplies, demands, costs


def save_results(filepath, problem, method_name):
    """
    Сохраняет результаты решения в файл
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(problem.get_detailed_report())


def print_problem_info(supplies, demands, costs):
    """
    Выводит информацию о задаче
    """
    print("\n" + "="*70)
    print("ИСХОДНЫЕ ДАННЫЕ ТРАНСПОРТНОЙ ЗАДАЧИ")
    print("="*70)

    print(f"\nЗапасы поставщиков: {supplies}")
    print(f"Спрос потребителей: {demands}")
    print(f"\nСумма запасов: {sum(supplies):.0f}")
    print(f"Сумма спроса: {sum(demands):.0f}")

    sum_supplies = sum(supplies)
    sum_demands = sum(demands)

    if abs(sum_supplies - sum_demands) < 0.001:
        print("✓ Задача сбалансирована")
    else:
        print("✗ Задача НЕ сбалансирована")
        diff = sum_supplies - sum_demands
        if diff > 0:
            print(f"  Избыток запасов: {diff:.0f}")
        else:
            print(f"  Дефицит товара: {-diff:.0f}")

    print("\nМатрица стоимостей доставки (д.е. за единицу):")
    print("-" * 70)

    header = "Поставщик |"
    for j in range(len(costs[0])):
        header += f" Потр.{j+1} |"
    print(header)
    print("-" * 70)

    for i, row in enumerate(costs):
        print(f"Завод {i+1}    |", end="")
        for cost in row:
            print(f" {cost:5.0f}  |", end="")
        print()

    print("-" * 70)
