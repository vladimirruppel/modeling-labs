from colorama import Fore, Style

def read_data(filename, num_machines=2):
    """Читает данные из файла и преобразует их в список словарей."""
    details = []
    try:
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                parts = list(map(int, line.strip().split()))
                detail = {'id': i + 1}
                if num_machines == 2 and len(parts) == 2:
                    detail['a'] = parts[0]
                    detail['b'] = parts[1]
                elif num_machines == 3 and len(parts) == 3:
                    detail['a'] = parts[0]
                    detail['b'] = parts[1]
                    detail['c'] = parts[2]
                else:
                    print(f"{Fore.RED}Ошибка: Неверный формат данных в строке {i+1} файла {filename}{Style.RESET_ALL}")
                    return None
                details.append(detail)
    except FileNotFoundError:
        print(f"{Fore.RED}Ошибка: Файл {filename} не найден.{Style.RESET_ALL}")
        return None
    return details

def print_details_table(details, title="Таблица деталей"):
    """Печатает таблицу с данными о деталях."""
    print(f"\n--- {title} ---")
    num_machines = 3 if 'c' in details[0] else 2
    
    if num_machines == 2:
        print("  id |  a  |  b  ")
        print("-----------------")
        for d in details:
            print(f"  {d['id']:<2} | {d['a']:<3} | {d['b']:<3} ")
    else: # num_machines == 3
        print("  id |  a  |  b  |  c  ")
        print("----------------------")
        for d in details:
            print(f"  {d['id']:<2} | {d['a']:<3} | {d['b']:<3} | {d['c']:<3} ")
    print("-" * (17 if num_machines == 2 else 22))

def print_sequence(sequence, title="Последовательность"):
    """Печатает последовательность обработки деталей."""
    ids = [d['id'] for d in sequence]
    print(f"\n{title}: {' -> '.join(map(str, ids))}")
