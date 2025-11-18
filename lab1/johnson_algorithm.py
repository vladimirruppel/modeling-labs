import itertools
from gantt_chart_gui import calculate_times # Импортируем функцию расчета времени

def johnson_nx2(details):
    """Реализация алгоритма Джонсона для n деталей и 2 станков."""
    
    # Создаем два списка: один для деталей с min(a,b) на станке A, другой - на B
    group1 = [] # a_i < b_i
    group2 = [] # a_i >= b_i

    for detail in details:
        if detail['a'] < detail['b']:
            group1.append(detail)
        else:
            group2.append(detail)
            
    # Сортируем первую группу по возрастанию a_i
    group1.sort(key=lambda x: x['a'])
    # Сортируем вторую группу по убыванию b_i
    group2.sort(key=lambda x: x['b'], reverse=True)
    
    # Оптимальная последовательность - это конкатенация двух групп
    return group1 + group2

def johnson_nx3(details):
    """
    Реализация алгоритма Джонсона для n деталей и 3 станков.
    Возвращает оптимальную последовательность или None, если условие не выполнено.
    """
    # 1. Проверка условия применимости алгоритма
    a_s = [d['a'] for d in details]
    b_s = [d['b'] for d in details]
    c_s = [d['c'] for d in details]
    
    condition1 = min(a_s) >= max(b_s)
    condition2 = min(c_s) >= max(b_s)
    
    if not (condition1 or condition2):
        print("\nУсловие Джонсона (min(a) >= max(b) или min(c) >= max(b)) не выполняется.")
        return None
        
    print("\nУсловие Джонсона выполняется. Сводим задачу к n x 2.")
    
    # 2. Сведение к задаче n x 2
    virtual_details = []
    for d in details:
        virtual_detail = {
            'id': d['id'],
            'a': d['a'] + d['b'], # Новое "a"
            'b': d['b'] + d['c'], # Новое "b"
            'original': d # Сохраняем ссылку на исходные данные
        }
        virtual_details.append(virtual_detail)
        
    # 3. Применяем алгоритм для n x 2 к виртуальным деталям
    virtual_optimal_seq = johnson_nx2(virtual_details)
    
    # 4. Восстанавливаем исходную последовательность
    optimal_sequence = [vd['original'] for vd in virtual_optimal_seq]
    
    return optimal_sequence


def brute_force_nx3(details):
    """
    Решение задачи n x 3 методом полного перебора всех перестановок.
    """
    if len(details) > 8: # Ограничение, чтобы избежать слишком долгого ожидания
        print("Полный перебор для > 8 деталей может занять очень много времени. Прервано.")
        return None

    best_sequence = None
    min_total_time = float('inf')
    
    # Генерируем все возможные последовательности (перестановки)
    sequences = list(itertools.permutations(details))
    print(f"\nНачинаем полный перебор. Всего вариантов: {len(sequences)}")

    for seq in sequences:
        # Для каждой последовательности считаем общее время
        timeline, total_time = calculate_times(list(seq), 3)
        if total_time < min_total_time:
            min_total_time = total_time
            best_sequence = list(seq)
            
    return best_sequence
