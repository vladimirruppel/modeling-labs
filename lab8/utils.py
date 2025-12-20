# -*- coding: utf-8 -*-
"""
Утилиты для вывода, форматирования и работы с данными.

Функции для вывода таблиц, выбора конфигураций, ввода параметров.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from config import DistributionType


# ============================================================================
# ФОРМАТИРОВАНИЕ И ВЫВОД
# ============================================================================

def print_separator(char: str = '=', width: int = 80) -> None:
    """Печать разделителя."""
    print(char * width)


def print_section_header(title: str, width: int = 80) -> None:
    """Печать заголовка секции."""
    print_separator('=', width)
    print(title.center(width))
    print_separator('=', width)


def print_subsection_header(title: str, width: int = 80) -> None:
    """Печать подзаголовка."""
    print(f"\n{title}")
    print_separator('-', width)


def format_value(value: float, precision: int = 4) -> str:
    """Форматировать числовое значение."""
    if isinstance(value, int):
        return str(value)
    return f"{value:.{precision}f}"


def print_results_table(data: Dict, title: str = "Результаты") -> None:
    """
    Печать таблицы результатов.

    Args:
        data: Словарь ключ->значение
        title: Заголовок таблицы
    """
    print_subsection_header(title)
    max_key_len = max(len(str(k)) for k in data.keys()) if data else 0

    for key, value in data.items():
        if isinstance(value, float):
            value_str = format_value(value, 6)
        elif isinstance(value, list) and value and isinstance(value[0], float):
            value_str = f"[{', '.join(format_value(v, 4) for v in value[:3])}...]"
        else:
            value_str = str(value)

        print(f"  {str(key):<{max_key_len}}: {value_str}")


def print_probabilities_table(probabilities: Dict[int, float],
                             max_states: int = 10) -> None:
    """
    Печать таблицы вероятностей состояний.

    Args:
        probabilities: Словарь состояние->вероятность
        max_states: Максимум состояний для вывода
    """
    print_subsection_header("Вероятности состояний")

    states = sorted(probabilities.keys())[:max_states]
    total_prob = sum(probabilities.get(s, 0) for s in states)

    for state in states:
        prob = probabilities.get(state, 0.0)
        bar_length = int(prob * 50)
        bar = '█' * bar_length + '░' * (50 - bar_length)
        print(f"  p_{state:2d} = {prob:.6f} |{bar}|")

    if len(probabilities) > max_states:
        rest_prob = sum(probabilities.get(s, 0) for s in
                       sorted(probabilities.keys())[max_states:])
        print(f"  ... ({len(probabilities) - max_states} more states, sum={rest_prob:.6f})")


def print_comparison_table(simulated: Dict, theoretical: Dict,
                          errors: Dict, title: str = "Сравнение") -> None:
    """
    Печать таблицы сравнения симуляции с теорией.

    Args:
        simulated: Симуляционные результаты
        theoretical: Теоретические результаты
        errors: Ошибки
        title: Заголовок
    """
    print_subsection_header(title)

    # Определить максимальную длину ключа
    all_keys = set(simulated.keys()) | set(theoretical.keys())
    max_key_len = max(len(str(k)) for k in all_keys) if all_keys else 0

    print(f"  {'Характеристика':<{max_key_len}} | "
          f"{'Теория':>12} | {'Симуляция':>12} | {'Ошибка':>10}")
    print_separator('-', max_key_len + 50)

    for key in sorted(all_keys):
        theory_val = theoretical.get(key, 0.0)
        sim_val = simulated.get(key, 0.0)
        error = errors.get(key, 0.0)

        if isinstance(theory_val, (int, float)) and isinstance(sim_val, (int, float)):
            print(f"  {str(key):<{max_key_len}} | "
                  f"{theory_val:>12.6f} | {sim_val:>12.6f} | {error*100:>8.2f}%")


# ============================================================================
# ВЫБОР КОНФИГУРАЦИИ И ПАРАМЕТРОВ
# ============================================================================

def input_menu_choice(options: Dict[int, str], prompt: str = "Выберите опцию") -> Optional[int]:
    """
    Интерактивный выбор из меню.

    Args:
        options: Словарь номер->описание опции
        prompt: Текст приглашения

    Returns:
        Выбранный номер или None если отмена
    """
    while True:
        print(f"\n{prompt}:")
        for num, desc in sorted(options.items()):
            print(f"  {num}. {desc}")

        try:
            choice = int(input("\nВаш выбор: ").strip())
            if choice in options:
                return choice
            else:
                print("❌ Некорректный выбор. Попробуйте снова.")
        except ValueError:
            print("❌ Пожалуйста, введите число.")
        except KeyboardInterrupt:
            print("\n⚠ Отмена операции.")
            return None


def input_distribution_choice() -> Optional[DistributionType]:
    """
    Интерактивный выбор распределения вероятности.

    Returns:
        Выбранный тип распределения или None
    """
    options = {
        1: "Экспоненциальное (показательное)",
        2: "Распределение Вейбула",
        3: "Гамма-распределение",
        4: "Нормальное (Гауссовское)",
    }

    choice = input_menu_choice(options, "Выберите распределение")

    mapping = {
        1: DistributionType.EXPONENTIAL,
        2: DistributionType.WEIBULL,
        3: DistributionType.GAMMA,
        4: DistributionType.NORMAL,
    }

    return mapping.get(choice)


def input_distribution_params(dist_type: DistributionType) -> Optional[Dict]:
    """
    Интерактивный ввод параметров распределения.

    Args:
        dist_type: Тип распределения

    Returns:
        Словарь с параметрами или None
    """
    try:
        if dist_type == DistributionType.EXPONENTIAL:
            print("\nПараметры экспоненциального распределения:")
            lambda_param = float(input("  Интенсивность λ (по умолчанию 0.4): ") or "0.4")
            return {'lambda_param': lambda_param}

        elif dist_type == DistributionType.WEIBULL:
            print("\nПараметры распределения Вейбула:")
            a = float(input("  Параметр формы a (по умолчанию 2.0): ") or "2.0")
            b = float(input("  Параметр масштаба b (по умолчанию 2.5): ") or "2.5")
            return {'a': a, 'b': b}

        elif dist_type == DistributionType.GAMMA:
            print("\nПараметры Гамма-распределения:")
            lambda_param = float(input("  Параметр λ (по умолчанию 0.4): ") or "0.4")
            eta = int(input("  Параметр η (целое число, по умолчанию 2): ") or "2")
            return {'lambda_param': lambda_param, 'eta': eta}

        elif dist_type == DistributionType.NORMAL:
            print("\nПараметры нормального распределения:")
            m = float(input("  Математическое ожидание m (по умолчанию 2.5): ") or "2.5")
            sigma = float(input("  Стандартное отклонение σ (по умолчанию 0.5): ") or "0.5")
            return {'m': m, 'sigma': sigma}

        return None

    except ValueError:
        print("❌ Ошибка при вводе параметров.")
        return None
    except KeyboardInterrupt:
        print("\n⚠ Отмена операции.")
        return None


def input_integer(prompt: str, default: int = None, min_val: int = 1) -> Optional[int]:
    """
    Интерактивный ввод целого числа.

    Args:
        prompt: Текст приглашения
        default: Значение по умолчанию
        min_val: Минимально допустимое значение

    Returns:
        Введённое число или None
    """
    try:
        default_str = f" (по умолчанию {default})" if default else ""
        value = input(f"{prompt}{default_str}: ").strip()

        if not value and default is not None:
            return default

        val = int(value)
        if val >= min_val:
            return val
        else:
            print(f"❌ Значение должно быть ≥ {min_val}")
            return None

    except ValueError:
        print("❌ Пожалуйста, введите целое число.")
        return None
    except KeyboardInterrupt:
        print("\n⚠ Отмена операции.")
        return None


def input_float(prompt: str, default: float = None, min_val: float = 0.0) -> Optional[float]:
    """
    Интерактивный ввод вещественного числа.

    Args:
        prompt: Текст приглашения
        default: Значение по умолчанию
        min_val: Минимально допустимое значение

    Returns:
        Введённое число или None
    """
    try:
        default_str = f" (по умолчанию {default})" if default else ""
        value = input(f"{prompt}{default_str}: ").strip()

        if not value and default is not None:
            return default

        val = float(value)
        if val > min_val:
            return val
        else:
            print(f"❌ Значение должно быть > {min_val}")
            return None

    except ValueError:
        print("❌ Пожалуйста, введите число.")
        return None
    except KeyboardInterrupt:
        print("\n⚠ Отмена операции.")
        return None


# ============================================================================
# РАБОТА С ДАННЫМИ И КОНФИГУРАЦИЯМИ
# ============================================================================

def load_variant18_config() -> Optional[Dict]:
    """
    Загрузить конфигурацию варианта 18 из JSON.

    Returns:
        Словарь с параметрами или None если ошибка
    """
    config_path = Path(__file__).parent / "data" / "variant_18_params.json"

    if not config_path.exists():
        print(f"❌ Файл конфигурации не найден: {config_path}")
        return None

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"❌ Ошибка при загрузке конфигурации: {e}")
        return None


def load_configuration(config_id: int) -> Optional[Dict]:
    """
    Загрузить конфигурацию по ID из варианта 18.

    Args:
        config_id: ID конфигурации (1, 2 или 3)

    Returns:
        Словарь с параметрами конфигурации или None
    """
    config = load_variant18_config()
    if not config:
        return None

    configs = config.get('configurations', [])
    for cfg in configs:
        if cfg.get('id') == config_id:
            return cfg

    print(f"❌ Конфигурация {config_id} не найдена.")
    return None


def save_results(results: Dict, filename: str) -> bool:
    """
    Сохранить результаты в JSON файл.

    Args:
        results: Словарь результатов
        filename: Имя файла

    Returns:
        True если успешно, False иначе
    """
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    filepath = output_dir / filename

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"✓ Результаты сохранены в {filepath}")
        return True
    except Exception as e:
        print(f"❌ Ошибка при сохранении результатов: {e}")
        return False


def display_progress(current: int, total: int, prefix: str = "Прогресс",
                    bar_length: int = 40) -> None:
    """
    Отобразить прогресс-бар.

    Args:
        current: Текущее значение
        total: Общее значение
        prefix: Текст префикса
        bar_length: Длина бара в символах
    """
    if total <= 0:
        return

    percent = current / total
    filled = int(bar_length * percent)
    bar = '█' * filled + '░' * (bar_length - filled)

    print(f"\r{prefix}: |{bar}| {percent*100:.1f}% ({current}/{total})", end='', flush=True)

    if current == total:
        print()  # Новая строка в конце


# ============================================================================
# ТЕСТИРОВАНИЕ
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("ТЕСТИРОВАНИЕ УТИЛИТ")
    print("=" * 70)

    # Тест 1: Загрузка конфигурации
    print("\n1. Загрузка конфигурации варианта 18")
    print("-" * 70)
    config = load_variant18_config()
    if config:
        print(f"✓ Загружена конфигурация {config.get('variant')}")
        print(f"  Описание: {config.get('description')}")
        print(f"  Число конфигураций: {len(config.get('configurations', []))}")

    # Тест 2: Загрузка отдельной конфигурации
    print("\n2. Загрузка конфигурации №1")
    print("-" * 70)
    cfg1 = load_configuration(1)
    if cfg1:
        print(f"✓ {cfg1.get('description')}")
        print(f"  n_channels: {cfg1.get('n_channels')}")
        print(f"  μ: {cfg1.get('mu')}")

    # Тест 3: Форматирование
    print("\n3. Форматирование значений")
    print("-" * 70)
    print(f"  {format_value(3.14159265, 4)}")
    print(f"  {format_value(0.00001234, 6)}")
    print(f"  {format_value(1000)}")

    # Тест 4: Таблица вероятностей
    print("\n4. Таблица вероятностей")
    print("-" * 70)
    probs = {0: 0.2, 1: 0.16, 2: 0.128, 3: 0.1024, 4: 0.08192}
    print_probabilities_table(probs, max_states=5)

    # Тест 5: Прогресс-бар
    print("\n5. Прогресс-бар")
    print("-" * 70)
    for i in range(11):
        display_progress(i, 10, "Выполнение")

    print("\n" + "=" * 70)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 70)
