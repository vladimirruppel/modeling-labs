"""Утилиты для работы с данными ЛР 2"""

def read_data(filepath, num_machines=None):
    """
    Чтение данных из файла.
    Формат: деталь_номер время1 время2 ... времяm

    Возвращает словарь:
    {
        'details': [1, 2, ..., n],
        'times': [[t11, t12, ..., t1m], ..., [tn1, tn2, ..., tnm]],
        'num_details': n,
        'num_machines': m
    }
    """
    details = []
    times = []

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = list(map(int, line.split()))
            detail_num = parts[0]
            detail_times = parts[1:]
            details.append(detail_num)
            times.append(detail_times)

    num_details = len(details)
    num_machines = len(times[0]) if times else 0

    return {
        'details': details,
        'times': times,
        'num_details': num_details,
        'num_machines': num_machines
    }


def print_table_header(num_machines):
    """Печать заголовка таблицы с временами обработки"""
    header = "d_i \\ станки"
    for j in range(1, num_machines + 1):
        header += f"\t{j}"
    header += "\tP_i1\tP_i2\tλ_i"
    return header


def print_times_table(details, times):
    """Печать таблицы времен обработки"""
    print("=" * 80)
    print("Таблица исходных данных (времена обработки на станках)")
    print("=" * 80)
    num_machines = len(times[0])

    header = "d_i \\ станки"
    for j in range(1, num_machines + 1):
        header += f"\t{j}"
    print(header)
    print("-" * 80)

    for i, detail in enumerate(details):
        row = f"{detail}"
        for time in times[i]:
            row += f"\t{time}"
        print(row)
    print("=" * 80)


def print_sequence(sequence, title="Последовательность"):
    """Печать последовательности запуска"""
    seq_str = " → ".join(map(str, sequence))
    print(f"{title}: {seq_str}")


def print_separator(char="=", width=100):
    """Печать разделителя"""
    print(char * width)


def print_section_header(text):
    """Печать заголовка секции"""
    print_separator("=")
    print(f"  {text}")
    print_separator("=")


def print_result_table(details, sequence, times, result, title="Таблица расчета времени"):
    """
    Красивый вывод таблицы расчета времени в формате t_ij / T_ij.

    Args:
        details: список номеров деталей
        sequence: последовательность запуска
        times: матрица времен обработки
        result: результаты матричного метода
        title: название таблицы
    """
    T = result['T']
    num_machines = len(times[0])
    detail_index = {details[i]: i for i in range(len(details))}

    print("\n" + "=" * 150)
    print(f"  {title}")
    print("=" * 150)

    # Заголовок таблицы
    header = "d_i \\ Станки"
    col_width = 12
    for j in range(1, num_machines + 1):
        header += f" | {j:^{col_width-3}}"
    header += f" | {'T_i^ож':^{col_width-3}}"
    print(header)
    print("-" * 150)

    # Данные по деталям
    for i, detail in enumerate(sequence):
        detail_idx = detail_index[detail]
        row = f"{detail:^12}"

        for j in range(num_machines):
            t_ij = times[detail_idx][j]
            T_ij = T[i][j]
            cell = f"{t_ij}/{T_ij}"
            row += f" | {cell:^{col_width-3}}"

        row += f" | {result['T_wait'][i]:^{col_width-3}}"
        print(row)

    # Строка простоя машин
    print("-" * 150)
    row = "T_j^пр".ljust(12)
    for j in range(num_machines):
        row += f" | {result['T_idle'][j]:^{col_width-3}}"
    row += f" | {'T^пр\\T^ож':^{col_width-3}}"
    print(row)

    # Итоговая строка
    print("-" * 150)
    print(f"Время цикла (T_nm):        {result['T_cycle']}")
    print(f"Суммарное время ожидания:  {result['T_wait_total']}")
    print(f"Суммарный простой машин:   {result['T_idle_total']}")
    print("=" * 150)
