"""Реализация 4 правил Петрова для генерации последовательностей"""


def rule1_petrov(details, P_i1, P_i2, lambda_i, subsets):
    """
    Правило 1: Первыми обрабатываются детали из D_1_0 по возрастанию P_i1,
    затем детали из D2 по убыванию P_i2.
    """
    sequence = []

    # Сортируем детали из D_1_0 по возрастанию P_i1
    D_1_0_sorted = sorted(
        subsets['D_1_0'],
        key=lambda i: (P_i1[i], lambda_i[i])  # при равных P_i1 сортируем по λ
    )
    sequence.extend([details[i] for i in D_1_0_sorted])

    # Сортируем детали из D2 по убыванию P_i2
    D2_sorted = sorted(
        subsets['D2'],
        key=lambda i: (-P_i2[i], -lambda_i[i])  # по убыванию P_i2
    )
    sequence.extend([details[i] for i in D2_sorted])

    return sequence


def rule2_petrov(details, lambda_i):
    """
    Правило 2: Детали упорядочиваются по убыванию λ_i.
    """
    # Сортируем все детали по убыванию λ
    indices = list(range(len(details)))
    indices_sorted = sorted(indices, key=lambda i: -lambda_i[i])

    sequence = [details[i] for i in indices_sorted]
    return sequence


def rule3_petrov(details, P_i1, P_i2, lambda_i, subsets):
    """
    Правило 3: Первыми детали из D1 по возрастанию P_i1,
    вторыми - детали из D0 по возрастанию P_i1,
    третьими - детали из D2 по убыванию P_i2.
    """
    sequence = []

    # D1 по возрастанию P_i1
    D1_sorted = sorted(
        subsets['D1'],
        key=lambda i: (P_i1[i], lambda_i[i])
    )
    sequence.extend([details[i] for i in D1_sorted])

    # D0 по возрастанию P_i1
    D0_sorted = sorted(
        subsets['D0'],
        key=lambda i: (P_i1[i], lambda_i[i])
    )
    sequence.extend([details[i] for i in D0_sorted])

    # D2 по убыванию P_i2
    D2_sorted = sorted(
        subsets['D2'],
        key=lambda i: (-P_i2[i], -lambda_i[i])
    )
    sequence.extend([details[i] for i in D2_sorted])

    return sequence


def rule4_petrov(details, P_i1, P_i2, lambda_i, subsets):
    """
    Правило 4: Попарное упорядочение внутри подмножеств.
    Наиболее сложное правило.
    """
    sequence = []
    used = set()

    # Обрабатываем подмножество D1
    D1_indices = subsets['D1'].copy()
    while D1_indices:
        if len(D1_indices) == 1:
            # Одна непарная деталь из D1
            idx = D1_indices.pop(0)
            sequence.append(details[idx])
            used.add(idx)
            break

        # Ищем первую деталь пары (максимальный P_i2)
        idx1 = max(D1_indices, key=lambda i: P_i2[i])
        D1_indices.remove(idx1)

        # Ищем вторую деталь пары (минимальный P_i1)
        idx2 = min(D1_indices, key=lambda i: P_i1[i])
        D1_indices.remove(idx2)

        sequence.append(details[idx1])
        sequence.append(details[idx2])
        used.add(idx1)
        used.add(idx2)

    # Обрабатываем подмножество D0
    D0_indices = subsets['D0'].copy()
    while D0_indices:
        if len(D0_indices) == 1:
            # Одна непарная деталь из D0
            idx = D0_indices.pop(0)
            sequence.append(details[idx])
            used.add(idx)
            break

        # Ищем первую деталь пары (максимальный P_i2)
        idx1 = max(D0_indices, key=lambda i: P_i2[i])
        D0_indices.remove(idx1)

        # Ищем вторую деталь пары (минимальный P_i1)
        idx2 = min(D0_indices, key=lambda i: P_i1[i])
        D0_indices.remove(idx2)

        sequence.append(details[idx1])
        sequence.append(details[idx2])
        used.add(idx1)
        used.add(idx2)

    # Обрабатываем подмножество D2
    D2_indices = subsets['D2'].copy()
    while D2_indices:
        if len(D2_indices) == 1:
            # Одна непарная деталь из D2
            idx = D2_indices.pop(0)
            sequence.append(details[idx])
            used.add(idx)
            break

        # Ищем первую деталь пары (максимальный P_i2)
        idx1 = max(D2_indices, key=lambda i: P_i2[i])
        D2_indices.remove(idx1)

        # Ищем вторую деталь пары (минимальный P_i1)
        idx2 = min(D2_indices, key=lambda i: P_i1[i])
        D2_indices.remove(idx2)

        sequence.append(details[idx1])
        sequence.append(details[idx2])
        used.add(idx1)
        used.add(idx2)

    return sequence


def generate_all_sequences(details, P_i1, P_i2, lambda_i, subsets):
    """Генерирование всех 4 последовательностей по правилам Петрова"""
    sequences = {
        1: rule1_petrov(details, P_i1, P_i2, lambda_i, subsets),
        2: rule2_petrov(details, lambda_i),
        3: rule3_petrov(details, P_i1, P_i2, lambda_i, subsets),
        4: rule4_petrov(details, P_i1, P_i2, lambda_i, subsets)
    }
    return sequences
