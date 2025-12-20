"""
Утилиты ввода/вывода для ЛР 7: Марковские СМО
"""

from colorama import Fore, Style


def print_section_header(title):
    """Выводит заголовок раздела с форматированием"""
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{title.center(60)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")


def print_separator(char='='):
    """Выводит разделитель"""
    print(f"{Fore.CYAN}{char*60}{Style.RESET_ALL}")


def input_intensity_or_time(param_name):
    """
    Получает ввод интенсивности или среднего времени.
    Возвращает интенсивность (в обратных единицах времени).
    """
    while True:
        print(f"\nДля параметра '{param_name}':")
        choice = input("Введите (л)и интенсивность или (в)ремя? [л/в]: ").strip().lower()

        if choice in ['л', 'intensity']:
            try:
                value = float(input(f"Введите {param_name} (интенсивность): "))
                if value <= 0:
                    print(f"{Fore.RED}Ошибка: значение должно быть положительным{Style.RESET_ALL}")
                    continue
                return value
            except ValueError:
                print(f"{Fore.RED}Ошибка: введите число{Style.RESET_ALL}")
                continue

        elif choice in ['в', 'time']:
            try:
                avg_time = float(input(f"Введите среднее время (минуты): "))
                if avg_time <= 0:
                    print(f"{Fore.RED}Ошибка: время должно быть положительным{Style.RESET_ALL}")
                    continue
                intensity = convert_time_to_intensity(avg_time)
                print(f"Интенсивность = 1/{avg_time:.4f} = {intensity:.4f} машин/мин")
                return intensity
            except ValueError:
                print(f"{Fore.RED}Ошибка: введите число{Style.RESET_ALL}")
                continue

        else:
            print(f"{Fore.RED}Ошибка: введите 'л' или 'в'{Style.RESET_ALL}")


def convert_time_to_intensity(avg_time):
    """
    Конвертирует среднее время в интенсивность.
    Формула: μ = 1 / среднее_время

    Args:
        avg_time: среднее время обслуживания (в минутах)

    Returns:
        Интенсивность обслуживания (машин/мин)
    """
    if avg_time <= 0:
        raise ValueError("Время должно быть положительным")
    return 1.0 / avg_time


def convert_intensity_to_time(intensity):
    """
    Конвертирует интенсивность в среднее время.
    Формула: T = 1 / μ

    Args:
        intensity: интенсивность (в обратных единицах времени)

    Returns:
        Среднее время обслуживания (в тех же единицах)
    """
    if intensity <= 0:
        raise ValueError("Интенсивность должна быть положительной")
    return 1.0 / intensity


def format_probability(prob):
    """
    Форматирует вероятность для вывода.

    Args:
        prob: вероятность (0 <= prob <= 1)

    Returns:
        Строка с форматированной вероятностью
    """
    if prob < 0 or prob > 1:
        return f"{prob:.6f}"

    if prob < 1e-6:
        return f"{prob:.2e}"
    elif prob < 0.001:
        return f"{prob:.6f}"
    else:
        return f"{prob:.6f}"


def format_value(value, decimals=4):
    """
    Форматирует числовое значение.

    Args:
        value: числовое значение
        decimals: количество знаков после запятой

    Returns:
        Строка с форматированным числом
    """
    if isinstance(value, float):
        if value == 0:
            return "0.0000"
        elif abs(value) < 0.0001:
            return f"{value:.2e}"
        else:
            return f"{value:.{decimals}f}"
    return str(value)


def print_results_table(results_dict, title=None):
    """
    Выводит таблицу результатов.

    Args:
        results_dict: словарь {название: значение}
        title: заголовок таблицы (опционально)
    """
    if title:
        print(f"\n{Fore.GREEN}{title}{Style.RESET_ALL}")

    print_separator()

    for key, value in results_dict.items():
        # Форматирование ключа
        display_key = key.replace('_', ' ').capitalize()

        # Форматирование значения
        if isinstance(value, (int, float)):
            if isinstance(value, float):
                display_value = format_value(value)
            else:
                display_value = str(value)
        else:
            display_value = str(value)

        # Вывод строки таблицы
        print(f"  {display_key:<35} {Fore.YELLOW}{display_value:>15}{Style.RESET_ALL}")

    print_separator()


def print_probabilities_table(probabilities_dict, title="Вероятности состояний"):
    """
    Выводит таблицу вероятностей состояний.

    Args:
        probabilities_dict: словарь {состояние: вероятность}
        title: заголовок таблицы
    """
    print(f"\n{Fore.GREEN}{title}{Style.RESET_ALL}")
    print_separator()

    for state, prob in probabilities_dict.items():
        prob_str = format_probability(prob)
        print(f"  P{state:<35} {Fore.YELLOW}{prob_str:>15}{Style.RESET_ALL}")

    print_separator()


def ask_continue():
    """
    Спрашивает пользователя, хочет ли он продолжить с новыми параметрами.

    Returns:
        True если нужно повторить, False если выход
    """
    while True:
        choice = input(f"\n{Fore.GREEN}Изменить параметры? (д/н): {Style.RESET_ALL}").strip().lower()
        if choice in ['д', 'yes', 'y']:
            return True
        elif choice in ['н', 'no', 'n']:
            return False
        else:
            print(f"{Fore.RED}Ошибка: введите 'д' или 'н'{Style.RESET_ALL}")


def ask_choice(prompt, options):
    """
    Спрашивает пользователя выбрать из предложенных вариантов.

    Args:
        prompt: текст вопроса
        options: список допустимых вариантов

    Returns:
        Выбранный вариант
    """
    while True:
        choice = input(f"\n{Fore.GREEN}{prompt}{Style.RESET_ALL}").strip()
        if choice in options:
            return choice
        else:
            print(f"{Fore.RED}Ошибка: выберите из {options}{Style.RESET_ALL}")


def print_stability_warning(lambda_val, mu, n_channels=1):
    """
    Выводит предупреждение, если система нестабильна.

    Args:
        lambda_val: интенсивность входящего потока
        mu: интенсивность обслуживания на один канал
        n_channels: количество каналов
    """
    rho = lambda_val / mu
    condition = rho / n_channels if n_channels > 1 else rho

    if n_channels == 1 and rho >= 1:
        print(f"\n{Fore.RED}⚠ ПРЕДУПРЕЖДЕНИЕ: ρ = {rho:.4f} >= 1{Style.RESET_ALL}")
        print(f"{Fore.RED}  Система нестабильна (очередь будет расти бесконечно){Style.RESET_ALL}")
    elif n_channels > 1 and condition >= 1:
        print(f"\n{Fore.RED}⚠ ПРЕДУПРЕЖДЕНИЕ: ρ/n = {condition:.4f} >= 1{Style.RESET_ALL}")
        print(f"{Fore.RED}  Система нестабильна (очередь будет расти бесконечно){Style.RESET_ALL}")
    else:
        print(f"\n{Fore.GREEN}✓ Система стабильна{Style.RESET_ALL}")
        print(f"  ρ = {rho:.4f}", end="")
        if n_channels > 1:
            print(f", ρ/n = {condition:.4f}")
        else:
            print()


def clear_screen():
    """Очищает экран консоли"""
    import os
    os.system('clear' if os.name != 'nt' else 'cls')
