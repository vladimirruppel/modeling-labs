from utils import read_data, print_details_table, print_sequence
from gantt_chart_gui import show_gantt_chart 
from johnson_algorithm import johnson_nx2, johnson_nx3, brute_force_nx3
from colorama import Fore, Style

# Константы с именами файлов
FILE_NX2 = "data/variant_nx2.txt"
FILE_NX3_JOHNSON = "data/variant_nx3.txt"
FILE_NX3_BF = "data/variant_nx3_bf.txt"

def run_task1():
    print(f"\n{Fore.CYAN}--- ЗАДАНИЕ 1: АЛГОРИТМ ДЖОНСОНА (n x 2) ---{Style.RESET_ALL}")
    details = read_data(FILE_NX2, num_machines=2)
    if not details: return

    print_details_table(details, "Исходные данные")
    
    print("\n>>> Открывается график Ганта для исходной последовательности...")
    print_sequence(details, "Исходная последовательность")

    show_gantt_chart(details, details, 
                     title="Исходная последовательность", 
                     filename="task1_initial.png")
    
    optimal_sequence = johnson_nx2(details)

    print_sequence(optimal_sequence, "Оптимальная последовательность")
    print_details_table(optimal_sequence, "Оптимальный порядок")
    
    print("\n>>> Открывается график Ганта для оптимальной последовательности...")
    
    show_gantt_chart(details, optimal_sequence, 
                     title="Оптимальная последовательность (Джонсон n x 2)", 
                     filename="task1_optimal.png")

def run_task2():
    print(f"\n{Fore.CYAN}--- ЗАДАНИЕ 2: АЛГОРИТМ ДЖОНСОНА (n x 3) ---{Style.RESET_ALL}")
    details = read_data(FILE_NX3_JOHNSON, num_machines=3)
    if not details: return

    print_details_table(details, "Исходные данные")

    print("\n>>> Открывается график Ганта для исходной последовательности...")
    print_sequence(details, "Исходная последовательность")
    show_gantt_chart(details, details, 
                     title="Исходная последовательность", 
                     filename="task2_initial.png")

    optimal_sequence = johnson_nx3(details)
    
    if optimal_sequence:
        print_sequence(optimal_sequence, "Оптимальная последовательность")
        print_details_table(optimal_sequence, "Оптимальный порядок")

        print("\n>>> Открывается график Ганта для оптимальной последовательности...")
        show_gantt_chart(details, optimal_sequence, 
                         title="Оптимальная последовательность (Джонсон n x 3)",
                         filename="task2_optimal.png")
    else:
        print(f"{Fore.YELLOW}Алгоритм Джонсона не может быть применен. Используйте метод полного перебора (Задание 3).{Style.RESET_ALL}")


def run_task3():
    print(f"\n{Fore.CYAN}--- ЗАДАНИЕ 3: ПОЛНЫЙ ПЕРЕБОР (n x 3) ---{Style.RESET_ALL}")
    details = read_data(FILE_NX3_BF, num_machines=3)
    if not details: return

    print_details_table(details, "Исходные данные")
    
    print("\n>>> Открывается график Ганта для исходной последовательности...")
    print_sequence(details, "Исходная последовательность")
    show_gantt_chart(details, details,
                     title="Исходная последовательность (для полного перебора)",
                     filename="task3_initial.png")

    print("\nПроверяем, можно ли применить алгоритм Джонсона...")
    if johnson_nx3(details) is not None:
         print(f"{Fore.YELLOW}Внимание: для этих данных условие Джонсона выполняется. Полный перебор все равно будет произведен.{Style.RESET_ALL}")

    optimal_sequence = brute_force_nx3(details)
    
    if optimal_sequence:
        print_sequence(optimal_sequence, "Оптимальная последовательность (полный перебор)")
        print_details_table(optimal_sequence, "Оптимальный порядок")

        print("\n>>> Открывается график Ганта для найденной оптимальной последовательности:")
        show_gantt_chart(details, optimal_sequence, 
                         title="Оптимальная последовательность (Полный перебор n x 3)",
                         filename="task3_optimal.png")

def main_menu():
    while True:
        print("\n" + "="*40)
        print("ЛАБОРАТОРНАЯ РАБОТА: ЗАДАЧА УПОРЯДОЧЕНИЯ")
        print("="*40)
        print("1. Задание 1: Алгоритм Джонсона (n x 2)")
        print("2. Задание 2: Алгоритм Джонсона (n x 3)")
        print("3. Задание 3: Полный перебор (n x 3)")
        print("0. Выход")
        print("="*40)
        
        choice = input("Выберите пункт меню: ")
        
        if choice == '1':
            run_task1()
        elif choice == '2':
            run_task2()
        elif choice == '3':
            run_task3()
        elif choice == '0':
            print("Выход из программы.")
            break
        else:
            print(f"{Fore.RED}Неверный ввод. Пожалуйста, выберите от 0 до 3.{Style.RESET_ALL}")


if __name__ == "__main__":
    main_menu()
