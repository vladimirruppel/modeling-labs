"""Матричный метод расчета времени обработки деталей"""


def calculate_processing_times(details, sequence, times):
    """
    Расчет времени окончания обработки для последовательности.

    Использует формулу:
    T_ij = t_ij + max(T_i-1,j; T_i,j-1)
    где T_ij - время окончания обработки i-й детали на j-й машине

    Args:
        details: список номеров деталей
        sequence: последовательность запуска (номера деталей)
        times: матрица времен [деталь][станок]

    Returns:
        {
            'T': [[T11, T12, ..., T1m], ...],  # матрица времен окончания
            'T_cycle': T_nm,  # время цикла (окончание на последней машине)
            'T_wait': [T1_ож, T2_ож, ...],  # время ожидания для каждой детали
            'T_wait_total': сумма,
            'T_idle': [T1_пр, T2_пр, ...],  # время простоя для каждой машины
            'T_idle_total': сумма
        }
    """
    num_machines = len(times[0])

    # Создаем индексный словарь для быстрого поиска
    detail_index = {details[i]: i for i in range(len(details))}

    # Переводим последовательность в индексы (в порядке обработки)
    sequence_indices = [detail_index[d] for d in sequence]

    # Инициализируем матрицу времен окончания
    T = [[0] * num_machines for _ in range(len(sequence))]

    # Расчет T_ij для каждой детали в порядке последовательности
    for i, detail_idx in enumerate(sequence_indices):
        for j in range(num_machines):
            t_ij = times[detail_idx][j]

            # Находим максимум времени окончания предыдущей детали на этой машине
            # или этой детали на предыдущей машине
            prev_detail_time = T[i - 1][j] if i > 0 else 0
            prev_machine_time = T[i][j - 1] if j > 0 else 0

            T[i][j] = t_ij + max(prev_detail_time, prev_machine_time)

    # Время цикла - время окончания последней детали на последней машине
    T_cycle = T[-1][-1]

    # Расчет времени ожидания для каждой детали
    T_wait = []
    for i, detail_idx in enumerate(sequence_indices):
        total_time = sum(times[detail_idx])
        wait_time = T[i][-1] - total_time
        T_wait.append(wait_time)

    T_wait_total = sum(T_wait)

    # Расчет времени простоя для каждой машины
    T_idle = []
    for j in range(num_machines):
        # Время простоя = время окончания последней операции на машине - сумма всех операций
        total_processing_time = sum(times[sequence_indices[i]][j] for i in range(len(sequence)))
        idle_time = T[-1][j] - total_processing_time
        T_idle.append(max(0, idle_time))  # Не может быть отрицательным

    T_idle_total = sum(T_idle)

    return {
        'T': T,
        'T_cycle': T_cycle,
        'T_wait': T_wait,
        'T_wait_total': T_wait_total,
        'T_idle': T_idle,
        'T_idle_total': T_idle_total,
        'sequence': sequence,
        'sequence_indices': sequence_indices
    }


def print_processing_table(details, sequence, times, result):
    """Печать таблицы с расчетом времени обработки"""
    T = result['T']
    num_machines = len(times[0])
    detail_index = {details[i]: i for i in range(len(details))}

    print("\nТаблица расчета времени обработки (t_ij / T_ij)")
    print("-" * (100 + num_machines * 20))

    # Заголовок
    header = "d_i \\ станки"
    for j in range(1, num_machines + 1):
        header += f"\t{j}"
    header += "\tT_i^ож"
    print(header)
    print("-" * (100 + num_machines * 20))

    # Данные
    for i, detail in enumerate(sequence):
        detail_idx = detail_index[detail]
        row = f"{detail}"
        for j in range(num_machines):
            t_ij = times[detail_idx][j]
            T_ij = T[i][j]
            row += f"\t{t_ij}/{T_ij}"
        row += f"\t{result['T_wait'][i]}"
        print(row)

    # Итоги
    row = "T_j^пр"
    T_idle_parts = []
    for j in range(num_machines):
        idle = 0
        for i in range(len(sequence)):
            if i == 0:
                machine_start = 0
            else:
                machine_start = T[i - 1][j]

            operation_start = T[i][j - 1] if j > 0 else 0
            idle += max(0, operation_start - machine_start -
                       (times[detail_index[sequence[i]]][j - 1] if j > 0 else 0))

        T_idle_parts.append(0)
        row += f"\t{T_idle_parts[j]}"

    row += f"\tT^пр\\T^ож"
    print(row)
    print(f"Время цикла (T_nm): {result['T_cycle']}")
    print(f"Суммарное время ожидания: {result['T_wait_total']}")
    print(f"Суммарный простой машин: {result['T_idle_total']}")


def compare_sequences(results):
    """
    Сравнение последовательностей и выбор оптимальной.

    Критерии:
    1. Минимальное время цикла T_cycle
    2. При равенстве - минимальное время ожидания T_wait_total
    3. При равенстве - минимальный простой T_idle_total

    Returns:
        индекс оптимальной последовательности и результаты
    """
    best_idx = None
    best_result = None

    for idx, result in enumerate(results):
        if best_idx is None:
            best_idx = idx
            best_result = result
        else:
            # Сравниваем по T_cycle
            if result['T_cycle'] < best_result['T_cycle']:
                best_idx = idx
                best_result = result
            # Если T_cycle равен, сравниваем по T_wait_total
            elif result['T_cycle'] == best_result['T_cycle']:
                if result['T_wait_total'] < best_result['T_wait_total']:
                    best_idx = idx
                    best_result = result
                # Если и T_wait_total равен, сравниваем по T_idle_total
                elif result['T_wait_total'] == best_result['T_wait_total']:
                    if result['T_idle_total'] < best_result['T_idle_total']:
                        best_idx = idx
                        best_result = result

    return best_idx, best_result
