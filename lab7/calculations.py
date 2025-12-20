"""
Математические вспомогательные функции для расчета характеристик СМО.
"""

import math


def calculate_factorial(n):
    """
    Вычисляет факториал n!

    Args:
        n: положительное целое число

    Returns:
        Факториал n
    """
    if n < 0:
        raise ValueError("Факториал не определен для отрицательных чисел")
    if n == 0 or n == 1:
        return 1
    return math.factorial(n)


def calculate_power(base, exponent):
    """
    Вычисляет base^exponent с защитой от переполнения.

    Args:
        base: основание степени
        exponent: показатель степени

    Returns:
        base^exponent
    """
    if base == 0:
        return 0 if exponent > 0 else float('inf')
    if exponent == 0:
        return 1.0

    try:
        result = math.pow(base, exponent)
        if result == float('inf') or result == 0:
            # Используем логарифмы для больших значений
            log_result = exponent * math.log(abs(base))
            if log_result > 700:  # Переполнение
                return float('inf')
            if log_result < -700:  # Подполнение
                return 0.0
        return result
    except (ValueError, OverflowError):
        if exponent > 0:
            return float('inf')
        else:
            return 0.0


def calculate_erlang_b(rho, n):
    """
    Вычисляет формулу Эрланга B (вероятность потери для M|M|n|0).

    Формула: B = (ρ^n / n!) / [1 + ρ/1! + ρ^2/2! + ... + ρ^n/n!]

    Args:
        rho: параметр ρ = λ/μ
        n: количество каналов

    Returns:
        Вероятность потери (0 <= B <= 1)
    """
    if rho < 0 or n < 1:
        raise ValueError("rho должно быть >= 0, n должно быть >= 1")

    # Вычисляем сумму в знаменателе: 1 + ρ/1! + ρ^2/2! + ... + ρ^n/n!
    denominator = 0.0
    for k in range(n + 1):
        term = calculate_power(rho, k) / calculate_factorial(k)
        if math.isfinite(term):
            denominator += term
        else:
            # Если числа слишком большие, формула не применима
            return 1.0 if rho > 1 else 0.0

    if denominator == 0:
        return 0.0

    # Вычисляем числитель: ρ^n / n!
    numerator = calculate_power(rho, n) / calculate_factorial(n)

    if not math.isfinite(numerator) or not math.isfinite(denominator):
        return 1.0 if rho > 1 else 0.0

    return numerator / denominator


def calculate_erlang_c(rho, n):
    """
    Вычисляет формулу Эрланга C (вероятность ожидания для M|M|n|∞).

    Формула: C = (ρ^n / n!) / [(ρ^n / n!) + (1 - ρ/n) * Σ(ρ^k / k!)]

    Args:
        rho: параметр ρ = λ/μ
        n: количество каналов

    Returns:
        Вероятность ожидания (0 <= C <= 1)
    """
    if rho < 0 or n < 1:
        raise ValueError("rho должно быть >= 0, n должно быть >= 1")

    condition = rho / n
    if condition >= 1:
        return 1.0  # Система нестабильна

    # Вычисляем формулу Эрланга B для n каналов
    erlang_b = calculate_erlang_b(rho, n)

    # Формула Эрланга C через B
    denominator = 1 - condition * (1 - erlang_b)
    if denominator == 0:
        return 1.0

    return erlang_b / denominator


def calculate_geometric_sum(rho, m):
    """
    Вычисляет сумму геометрической прогрессии для конечной очереди.

    Сумма: 1 + ρ + ρ^2 + ... + ρ^m = (1 - ρ^(m+1)) / (1 - ρ) при ρ ≠ 1
    Сумма: m + 1 при ρ = 1

    Args:
        rho: параметр ρ (знаменатель прогрессии)
        m: количество членов (начиная с 0)

    Returns:
        Сумма геометрической прогрессии
    """
    if m < 0:
        return 0.0

    if abs(rho - 1.0) < 1e-10:  # rho ≈ 1
        return float(m + 1)

    if abs(rho) < 1e-10:  # rho ≈ 0
        return 1.0

    try:
        numerator = 1.0 - calculate_power(rho, m + 1)
        denominator = 1.0 - rho

        if denominator == 0:
            return float(m + 1)

        return numerator / denominator
    except (ValueError, OverflowError):
        # Если rho > 1, сумма расходится
        if rho > 1:
            return float('inf')
        else:
            return 1.0 / (1.0 - rho)


def calculate_economic_costs(config_num, n_employees, n_channels, throughput,
                            revenue_per_customer=1000,
                            salary_per_hour=1000,
                            channel_cost_per_hour=20000):
    """
    Вычисляет экономические показатели для конфигурации.

    Args:
        config_num: номер конфигурации (для отчета)
        n_employees: количество служащих
        n_channels: количество каналов обслуживания
        throughput: абсолютная пропускная способность (машин/час или клиентов/час)
        revenue_per_customer: доход на одного клиента (руб)
        salary_per_hour: зарплата одного служащего в час (руб)
        channel_cost_per_hour: стоимость одного канала в час (руб)

    Returns:
        Словарь с экономическими показателями:
        {
            'config_num': номер конфигурации,
            'n_employees': количество служащих,
            'n_channels': количество каналов,
            'salary_costs': зарплата в час,
            'channel_costs': стоимость каналов в час,
            'total_costs': общие затраты в час,
            'throughput_per_hour': пропускная способность в час,
            'revenue': доход в час,
            'profit': прибыль в час,
            'profit_per_channel': прибыль на канал,
            'roi': return on investment (процент)
        }
    """
    # Конвертируем интенсивность в единицы в час
    if throughput < 1:  # Предполагаем, что указано в минутах, конвертируем в час
        throughput_per_hour = throughput * 60
    else:
        throughput_per_hour = throughput

    # Расчет затрат
    salary_costs = n_employees * salary_per_hour
    channel_costs = n_channels * channel_cost_per_hour
    total_costs = salary_costs + channel_costs

    # Расчет доходов
    revenue = throughput_per_hour * revenue_per_customer

    # Расчет прибыли
    profit = revenue - total_costs

    # Дополнительные показатели
    profit_per_channel = profit / n_channels if n_channels > 0 else 0
    roi = (profit / total_costs * 100) if total_costs > 0 else 0

    return {
        'config_num': config_num,
        'n_employees': n_employees,
        'n_channels': n_channels,
        'salary_costs': salary_costs,
        'channel_costs': channel_costs,
        'total_costs': total_costs,
        'throughput_per_hour': throughput_per_hour,
        'revenue': revenue,
        'profit': profit,
        'profit_per_channel': profit_per_channel,
        'roi': roi
    }


def check_stability_condition(lambda_val, mu, n_channels=1):
    """
    Проверяет условие стабильности системы.

    Для M|M|1|∞: требуется ρ = λ/μ < 1
    Для M|M|n|∞: требуется ρ/n = λ/(n*μ) < 1

    Args:
        lambda_val: интенсивность входящего потока
        mu: интенсивность обслуживания одного канала
        n_channels: количество каналов

    Returns:
        Кортеж (is_stable: bool, rho: float, condition: float)
    """
    if mu == 0:
        return False, float('inf'), float('inf')

    rho = lambda_val / mu
    condition = rho / n_channels if n_channels > 1 else rho

    is_stable = condition < 1

    return is_stable, rho, condition


def round_to_significant_figures(value, n_figures=6):
    """
    Округляет значение до заданного количества значащих цифр.

    Args:
        value: числовое значение
        n_figures: количество значащих цифр

    Returns:
        Округленное значение
    """
    if value == 0:
        return 0.0

    return round(value, -int(math.floor(math.log10(abs(value)))) + (n_figures - 1))


def format_scientific(value, n_figures=3):
    """
    Форматирует значение в научной нотации.

    Args:
        value: числовое значение
        n_figures: количество значащих цифр

    Returns:
        Строка в научной нотации
    """
    if value == 0:
        return "0"
    return f"{value:.{n_figures}e}"
