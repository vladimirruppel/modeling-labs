"""Полный перебор для поиска оптимальной последовательности"""

from itertools import permutations
from matrix_method import calculate_processing_times


def brute_force_search(details, times, max_items=8):
    """
    Полный перебор всех возможных последовательностей обработки.

    Примечание: метод имеет сложность O(n!), поэтому рекомендуется
    использовать только для n <= 8.

    Args:
        details: список номеров деталей
        times: матрица времен обработки
        max_items: максимальное количество деталей для перебора

    Returns:
        {
            'best_sequence': лучшая последовательность,
            'best_result': результаты расчета для лучшей,
            'all_results': словарь со всеми результатами
        }
    """
    num_details = len(details)

    if num_details > max_items:
        print(f"Внимание: перебор для {num_details} деталей может быть длительным!")
        response = input("Продолжить? (y/n): ")
        if response.lower() != 'y':
            return None

    print(f"\nПолный перебор {num_details} деталей ({num_details}! = {factorial(num_details)} вариантов)...")

    best_result = None
    best_sequence = None
    all_results = {}

    # Генерируем все перестановки
    for perm in permutations(details):
        result = calculate_processing_times(details, list(perm), times)

        seq_str = ' → '.join(map(str, perm))
        all_results[seq_str] = result

        # Сравниваем с лучшим результатом
        if best_result is None:
            best_result = result
            best_sequence = list(perm)
        else:
            # Критерий 1: минимальный T_cycle
            if result['T_cycle'] < best_result['T_cycle']:
                best_result = result
                best_sequence = list(perm)
            # Критерий 2: если T_cycle равен, минимальный T_wait_total
            elif result['T_cycle'] == best_result['T_cycle']:
                if result['T_wait_total'] < best_result['T_wait_total']:
                    best_result = result
                    best_sequence = list(perm)
                # Критерий 3: если все равно, минимальный T_idle_total
                elif result['T_wait_total'] == best_result['T_wait_total']:
                    if result['T_idle_total'] < best_result['T_idle_total']:
                        best_result = result
                        best_sequence = list(perm)

    return {
        'best_sequence': best_sequence,
        'best_result': best_result,
        'all_results': all_results
    }


def factorial(n):
    """Вычисление факториала"""
    if n <= 1:
        return 1
    return n * factorial(n - 1)


def print_brute_force_results(bf_results, top_count=5):
    """Печать результатов полного перебора"""
    if bf_results is None:
        return

    print("\n" + "=" * 100)
    print("РЕЗУЛЬТАТЫ ПОЛНОГО ПЕРЕБОРА")
    print("=" * 100)

    print(f"\nОптимальная последовательность: {' → '.join(map(str, bf_results['best_sequence']))}")
    print(f"Время цикла: {bf_results['best_result']['T_cycle']}")
    print(f"Время ожидания: {bf_results['best_result']['T_wait_total']}")
    print(f"Простой машин: {bf_results['best_result']['T_idle_total']}")

    # Сортируем результаты по T_cycle, затем по T_wait_total
    sorted_results = sorted(
        bf_results['all_results'].items(),
        key=lambda x: (x[1]['T_cycle'], x[1]['T_wait_total'], x[1]['T_idle_total'])
    )

    print(f"\nТоп {min(top_count, len(sorted_results))} последовательностей:")
    print("-" * 100)
    print("Последовательность\t\tT_цикл\tT_ожид\tT_пр")
    print("-" * 100)

    for i, (seq_str, result) in enumerate(sorted_results[:top_count]):
        print(f"{seq_str:<40}\t{result['T_cycle']}\t{result['T_wait_total']}\t{result['T_idle_total']}")

    print("=" * 100)
