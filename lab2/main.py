import os
import sys
import random
from pathlib import Path

# Импортируем модули
from utils import read_data, print_times_table, print_section_header, print_separator, print_result_table
from petrov_params import calculate_petrov_parameters, get_subsets, print_parameters_table
from petrov_rules import generate_all_sequences
from matrix_method import calculate_processing_times, print_processing_table, compare_sequences
from gantt_chart import save_gantt_chart
from brute_force import brute_force_search, print_brute_force_results
from colorama import Fore, Back, Style

# Константы
DATA_DIR = Path(__file__).parent / 'data'
OUTPUT_DIR = Path(__file__).parent / 'output_charts'
VARIANT = 18

FILE_DATA = DATA_DIR / f'variant_{VARIANT}.txt'


def main_menu():
    """Главное меню программы"""
    while True:
        print_separator("=")
        print(f"{Fore.CYAN}ЛАБОРАТОРНАЯ РАБОТА №2{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Модель задачи упорядочения n×m{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Вариант: {VARIANT}{Style.RESET_ALL}")
        print_separator("=")
        print("\nВыберите действие:")
        print("1. Запустить полный анализ (все методы)")
        print("2. Показать исходные данные")
        print("3. Вычислить параметры Петрова")
        print("4. Применить правила Петрова")
        print("5. Матричный метод расчета времени")
        print("6. Полный перебор (brute force)")
        print("7. Исходная последовательность (1,2,3...)")
        print("8. Случайная последовательность")
        print("9. Сравнить все методы")
        print("10. Выход")
        print_separator()

        choice = input("Введите номер действия (1-10): ").strip()

        if choice == '1':
            run_full_analysis()
        elif choice == '2':
            show_input_data()
        elif choice == '3':
            show_petrov_parameters()
        elif choice == '4':
            show_petrov_rules()
        elif choice == '5':
            show_matrix_method()
        elif choice == '6':
            show_brute_force()
        elif choice == '7':
            show_initial_sequence()
        elif choice == '8':
            show_random_sequence()
        elif choice == '9':
            compare_all_methods()
        elif choice == '10':
            print(f"\n{Fore.GREEN}До свидания!{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED}Неверный выбор. Попробуйте снова.{Style.RESET_ALL}")

        input("\nНажмите Enter для продолжения...")


def load_data():
    """Загрузка данных из файла"""
    if not FILE_DATA.exists():
        print(f"{Fore.RED}Ошибка: файл {FILE_DATA} не найден!{Style.RESET_ALL}")
        return None

    data = read_data(str(FILE_DATA))
    return data


def show_input_data():
    """Показать исходные данные"""
    data = load_data()
    if data is None:
        return

    print_section_header("ИСХОДНЫЕ ДАННЫЕ")
    print_times_table(data['details'], data['times'])
    print(f"Количество деталей (n): {data['num_details']}")
    print(f"Количество станков (m): {data['num_machines']}")


def show_petrov_parameters():
    """Показать параметры Петрова"""
    data = load_data()
    if data is None:
        return

    params = calculate_petrov_parameters(data['times'])
    subsets = get_subsets(params['lambda'], data['num_details'])

    print_section_header("ПАРАМЕТРЫ ПЕТРОВА")
    print_parameters_table(
        data['details'],
        data['times'],
        params['P_i1'],
        params['P_i2'],
        params['lambda']
    )

    print(f"\n{Fore.CYAN}Подмножества:{Style.RESET_ALL}")
    print(f"D1 (λ > 0):  {[data['details'][i] for i in subsets['D1']]}")
    print(f"D0 (λ = 0):  {[data['details'][i] for i in subsets['D0']]}")
    print(f"D2 (λ < 0):  {[data['details'][i] for i in subsets['D2']]}")
    print(f"D_1,0:       {[data['details'][i] for i in subsets['D_1_0']]}")


def show_petrov_rules():
    """Показать последовательности по правилам Петрова"""
    data = load_data()
    if data is None:
        return

    params = calculate_petrov_parameters(data['times'])
    subsets = get_subsets(params['lambda'], data['num_details'])
    sequences = generate_all_sequences(
        data['details'],
        params['P_i1'],
        params['P_i2'],
        params['lambda'],
        subsets
    )

    print_section_header("ПРАВИЛА ПЕТРОВА")

    for rule_num in range(1, 5):
        seq = sequences[rule_num]
        result = calculate_processing_times(data['details'], seq, data['times'])

        print(f"\n{Fore.CYAN}Правило {rule_num}:{Style.RESET_ALL}")
        print(f"Последовательность: {' → '.join(map(str, seq))}")
        print(f"Время цикла (T_nm): {Fore.YELLOW}{result['T_cycle']}{Style.RESET_ALL}")
        print(f"Время ожидания: {result['T_wait_total']}")
        print(f"Простой машин: {result['T_idle_total']}")


def show_matrix_method():
    """Показать матричный метод расчета"""
    data = load_data()
    if data is None:
        return

    params = calculate_petrov_parameters(data['times'])
    subsets = get_subsets(params['lambda'], data['num_details'])
    sequences = generate_all_sequences(
        data['details'],
        params['P_i1'],
        params['P_i2'],
        params['lambda'],
        subsets
    )

    print_section_header("МАТРИЧНЫЙ МЕТОД РАСЧЕТА")

    results = []
    for rule_num in range(1, 5):
        seq = sequences[rule_num]
        result = calculate_processing_times(data['details'], seq, data['times'])
        results.append(result)

        print(f"\n{Fore.CYAN}Правило {rule_num}: {' → '.join(map(str, seq))}{Style.RESET_ALL}")
        print_result_table(
            data['details'],
            seq,
            data['times'],
            result,
            f"Таблица расчета времени - Правило {rule_num}"
        )

    # Выбираем лучшую
    best_idx, best_result = compare_sequences(results)

    print(f"\n{Fore.GREEN}ОПТИМАЛЬНАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ (по Петрову):{Style.RESET_ALL}")
    print(f"Правило: {best_idx + 1}")
    print(f"Последовательность: {' → '.join(map(str, best_result['sequence']))}")
    print(f"Время цикла: {Fore.YELLOW}{best_result['T_cycle']}{Style.RESET_ALL}")


def show_brute_force():
    """Показать результаты полного перебора"""
    data = load_data()
    if data is None:
        return

    print_section_header("ПОЛНЫЙ ПЕРЕБОР")

    bf_results = brute_force_search(data['details'], data['times'])
    if bf_results:
        print_brute_force_results(bf_results, top_count=5)

        # Показываем таблицу для оптимальной последовательности
        print(f"\n{Fore.GREEN}ПОДРОБНАЯ ТАБЛИЦА ОПТИМАЛЬНОЙ ПОСЛЕДОВАТЕЛЬНОСТИ:{Style.RESET_ALL}")
        print(f"Последовательность: {' → '.join(map(str, bf_results['best_sequence']))}")
        print_result_table(
            data['details'],
            bf_results['best_sequence'],
            data['times'],
            bf_results['best_result'],
            "Таблица расчета времени - Оптимальная последовательность (полный перебор)"
        )


def compare_all_methods():
    """Сравнить все методы"""
    data = load_data()
    if data is None:
        return

    print_section_header("СРАВНЕНИЕ ВСЕХ МЕТОДОВ")

    # Вычисляем параметры
    params = calculate_petrov_parameters(data['times'])
    subsets = get_subsets(params['lambda'], data['num_details'])

    # Петровские последовательности
    sequences = generate_all_sequences(
        data['details'],
        params['P_i1'],
        params['P_i2'],
        params['lambda'],
        subsets
    )

    results = {}
    print(f"\n{Fore.CYAN}Расчет для всех правил Петрова...{Style.RESET_ALL}")

    for rule_num in range(1, 5):
        seq = sequences[rule_num]
        result = calculate_processing_times(data['details'], seq, data['times'])
        results[f'Правило {rule_num}'] = result

    # Полный перебор
    print(f"{Fore.CYAN}Полный перебор...{Style.RESET_ALL}")
    bf_results = brute_force_search(data['details'], data['times'], max_items=8)

    if bf_results:
        best_bf_seq = bf_results['best_sequence']
        results['Полный перебор'] = bf_results['best_result']

    # Выводим сравнение
    print("\n" + "=" * 100)
    print(f"{'Метод':<20} {'Последовательность':<50} {'T_цикл':<10} {'T_ожид':<10} {'T_пр':<10}")
    print("=" * 100)

    for method_name, result in results.items():
        seq_str = ' → '.join(map(str, result['sequence']))
        print(f"{method_name:<20} {seq_str:<50} {result['T_cycle']:<10} "
              f"{result['T_wait_total']:<10} {result['T_idle_total']:<10}")

    print("=" * 100)

    # Находим лучший результат
    best_method = min(results.items(),
                      key=lambda x: (x[1]['T_cycle'], x[1]['T_wait_total'], x[1]['T_idle_total']))

    print(f"\n{Fore.GREEN}ЛУЧШИЙ РЕЗУЛЬТАТ:{Style.RESET_ALL}")
    print(f"Метод: {best_method[0]}")
    print(f"Последовательность: {' → '.join(map(str, best_method[1]['sequence']))}")
    print(f"Время цикла: {Fore.YELLOW}{best_method[1]['T_cycle']}{Style.RESET_ALL}")

    # Сохраняем диаграмму Ганта
    if OUTPUT_DIR.exists():
        filename = OUTPUT_DIR / f'gantt_optimal_{best_method[1]["T_cycle"]}.png'
        print(f"\nСохранение диаграммы Ганта...")
        save_gantt_chart(
            data['details'],
            best_method[1]['sequence'],
            data['times'],
            best_method[1],
            f"График Ганта - {best_method[0]}",
            str(filename)
        )


def show_initial_sequence():
    """Показать результаты для исходной последовательности (1,2,3,4,5,6,7,...)"""
    data = load_data()
    if data is None:
        return

    print_section_header("ИСХОДНАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ")

    # Исходная последовательность - просто по порядку номеров
    initial_seq = sorted(data['details'])
    result = calculate_processing_times(data['details'], initial_seq, data['times'])

    print(f"\n{Fore.CYAN}Исходная последовательность (по порядку): {' → '.join(map(str, initial_seq))}{Style.RESET_ALL}")
    print_result_table(
        data['details'],
        initial_seq,
        data['times'],
        result,
        "Таблица расчета времени - Исходная последовательность"
    )


def show_random_sequence():
    """Показать результаты для случайной последовательности"""
    data = load_data()
    if data is None:
        return

    print_section_header("СЛУЧАЙНАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ")

    # Генерируем случайную перестановку
    random_seq = data['details'].copy()
    random.shuffle(random_seq)
    result = calculate_processing_times(data['details'], random_seq, data['times'])

    print(f"\n{Fore.CYAN}Случайная последовательность: {' → '.join(map(str, random_seq))}{Style.RESET_ALL}")
    print_result_table(
        data['details'],
        random_seq,
        data['times'],
        result,
        "Таблица расчета времени - Случайная последовательность"
    )


def run_full_analysis():
    """Запустить полный анализ"""
    data = load_data()
    if data is None:
        return

    print_section_header("ПОЛНЫЙ АНАЛИЗ")

    # Показываем исходные данные
    print(f"\n{Fore.CYAN}1. ИСХОДНЫЕ ДАННЫЕ{Style.RESET_ALL}")
    print_times_table(data['details'], data['times'])

    # Параметры Петрова
    print(f"\n{Fore.CYAN}2. ПАРАМЕТРЫ ПЕТРОВА{Style.RESET_ALL}")
    params = calculate_petrov_parameters(data['times'])
    subsets = get_subsets(params['lambda'], data['num_details'])
    print_parameters_table(
        data['details'],
        data['times'],
        params['P_i1'],
        params['P_i2'],
        params['lambda']
    )

    # Правила Петрова
    print(f"\n{Fore.CYAN}3. ПРАВИЛА ПЕТРОВА{Style.RESET_ALL}")
    sequences = generate_all_sequences(
        data['details'],
        params['P_i1'],
        params['P_i2'],
        params['lambda'],
        subsets
    )

    results = []
    for rule_num in range(1, 5):
        seq = sequences[rule_num]
        result = calculate_processing_times(data['details'], seq, data['times'])
        results.append(result)

        print(f"\n{Fore.CYAN}Правило {rule_num}:{Style.RESET_ALL}")
        print(f"Последовательность: {' → '.join(map(str, seq))}")
        print(f"Время цикла: {Fore.YELLOW}{result['T_cycle']}{Style.RESET_ALL}")

    # Сравнение и выбор лучшей
    best_idx, best_result = compare_sequences(results)

    print(f"\n{Fore.GREEN}ЛУЧШАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ ПО ПЕТРОВУ:{Style.RESET_ALL}")
    print(f"Правило {best_idx + 1}: {' → '.join(map(str, best_result['sequence']))}")
    print(f"Время цикла: {Fore.YELLOW}{best_result['T_cycle']}{Style.RESET_ALL}")

    # Полный перебор
    print(f"\n{Fore.CYAN}4. ПОЛНЫЙ ПЕРЕБОР{Style.RESET_ALL}")
    bf_results = brute_force_search(data['details'], data['times'], max_items=8)

    if bf_results:
        print(f"\n{Fore.GREEN}ОПТИМАЛЬНАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ (полный перебор):{Style.RESET_ALL}")
        print(f"Последовательность: {' → '.join(map(str, bf_results['best_sequence']))}")
        print(f"Время цикла: {Fore.YELLOW}{bf_results['best_result']['T_cycle']}{Style.RESET_ALL}")

        # Выбираем итоговую лучшую
        if bf_results['best_result']['T_cycle'] <= best_result['T_cycle']:
            final_result = bf_results['best_result']
            final_method = "Полный перебор"
        else:
            final_result = best_result
            final_method = f"Правило Петрова {best_idx + 1}"
    else:
        final_result = best_result
        final_method = f"Правило Петрова {best_idx + 1}"

    # Сохраняем диаграмму
    print(f"\n{Fore.CYAN}5. ДИАГРАММА ГАНТА{Style.RESET_ALL}")
    if OUTPUT_DIR.exists():
        filename = OUTPUT_DIR / f'gantt_optimal_{final_result["T_cycle"]}.png'
        print(f"Сохранение диаграммы Ганта...")
        try:
            save_gantt_chart(
                data['details'],
                final_result['sequence'],
                data['times'],
                final_result,
                f"График Ганта - {final_method} (T={final_result['T_cycle']})",
                str(filename)
            )
        except Exception as e:
            print(f"{Fore.YELLOW}Внимание: ошибка при сохранении диаграммы: {e}{Style.RESET_ALL}")

    print(f"\n{Fore.GREEN}ИТОГОВЫЙ РЕЗУЛЬТАТ:{Style.RESET_ALL}")
    print(f"Метод: {final_method}")
    print(f"Последовательность: {' → '.join(map(str, final_result['sequence']))}")
    print(f"Время цикла: {Fore.YELLOW}{final_result['T_cycle']}{Style.RESET_ALL}")
    print(f"Время ожидания: {final_result['T_wait_total']}")
    print(f"Простой машин: {final_result['T_idle_total']}")


if __name__ == '__main__':
    try:
        # Проверяем наличие выходной директории
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        main_menu()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Программа прервана пользователем.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Ошибка: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
