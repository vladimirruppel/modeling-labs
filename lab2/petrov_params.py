"""Вычисление параметров правил Петрова"""


def calculate_petrov_parameters(times):
    """
    Вычисление параметров Петрова: P_i1, P_i2, λ_i

    Args:
        times: список списков времен обработки [[t11, t12, ..., t1m], ...]

    Returns:
        {
            'P_i1': [P11, P12, ...],
            'P_i2': [P21, P22, ...],
            'lambda': [λ1, λ2, ...]
        }
    """
    n = len(times)  # количество деталей
    m = len(times[0]) if times else 0  # количество станков

    P_i1 = []
    P_i2 = []
    lambda_i = []

    for i in range(n):
        # Вычисление P_i1: сумма времен первых m/2 станков
        if m % 2 == 0:
            # m четно: P_i1 = сумма от j=1 до m/2
            p1 = sum(times[i][:m // 2])
        else:
            # m нечетно: P_i1 = сумма от j=1 до (m+1)/2
            p1 = sum(times[i][:m // 2 + 1])

        # Вычисление P_i2: сумма времен последних m/2 станков
        if m % 2 == 0:
            # m четно: P_i2 = сумма от j=m/2+1 до m
            p2 = sum(times[i][m // 2:])
        else:
            # m нечетно: P_i2 = сумма от j=(m+1)/2+1 до m
            p2 = sum(times[i][m // 2 + 1:])

        # Вычисление λ_i
        lam = p2 - p1

        P_i1.append(p1)
        P_i2.append(p2)
        lambda_i.append(lam)

    return {
        'P_i1': P_i1,
        'P_i2': P_i2,
        'lambda': lambda_i
    }


def get_subsets(lambda_i, num_details):
    """
    Определение подмножеств D1, D0, D2 на основе λ_i

    Args:
        lambda_i: список значений λ
        num_details: количество деталей

    Returns:
        {
            'D1': [индексы деталей где λ > 0],
            'D0': [индексы деталей где λ = 0],
            'D2': [индексы деталей где λ < 0],
            'D_1_0': [D1 ∪ D0]
        }
    """
    D1 = []  # λ > 0
    D0 = []  # λ = 0
    D2 = []  # λ < 0

    for i in range(num_details):
        if lambda_i[i] > 0:
            D1.append(i)
        elif lambda_i[i] == 0:
            D0.append(i)
        else:
            D2.append(i)

    D_1_0 = D1 + D0

    return {
        'D1': D1,
        'D0': D0,
        'D2': D2,
        'D_1_0': D_1_0
    }


def print_parameters_table(details, times, P_i1, P_i2, lambda_i):
    """Печать таблицы параметров Петрова"""
    print("\n" + "=" * 120)
    print("Таблица параметров Петрова")
    print("=" * 120)

    num_machines = len(times[0])
    header = "d_i \\ станки"
    for j in range(1, num_machines + 1):
        header += f"\t{j}"
    header += "\tP_i1\tP_i2\tλ_i"

    print(header)
    print("-" * 120)

    for i, detail in enumerate(details):
        row = f"{detail}"
        for time in times[i]:
            row += f"\t{time}"
        row += f"\t{P_i1[i]}\t{P_i2[i]}\t{lambda_i[i]}"
        print(row)

    print("=" * 120)
