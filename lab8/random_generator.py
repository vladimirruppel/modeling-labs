# -*- coding: utf-8 -*-
"""
Генератор случайных величин для различных распределений вероятности.

Поддерживаемые распределения:
- Экспоненциальное (показательное)
- Вейбула
- Гамма-распределение
- Нормальное (Гауссовское)

Формулы из ЛР №8 PDF (стр. 6)
"""

import random
import math
from typing import Union
from config import DistributionType


class RandomGenerator:
    """
    Генератор случайных величин для различных распределений.

    Все методы используют встроенный модуль random для генерации
    равномерно распределённых величин U(0,1).
    """

    def __init__(self, seed: int = None):
        """
        Инициализация генератора с опциональным seed для воспроизводимости.

        Args:
            seed: Начальное значение (для воспроизводимости).
                  Если None, используется текущее системное время.
        """
        if seed is not None:
            random.seed(seed)

    # ========================================================================
    # ЭКСПОНЕНЦИАЛЬНОЕ РАСПРЕДЕЛЕНИЕ
    # ========================================================================

    def generate_exponential(self, lambda_param: float) -> float:
        """
        Генерирует случайную величину, распределённую экспоненциально.

        Формула: x = -(1/λ) * ln(R)
        где R ~ U(0,1), λ - интенсивность

        Args:
            lambda_param: Интенсивность потока λ

        Returns:
            Случайная величина, распределённая экспоненциально

        Raises:
            ValueError: Если λ <= 0
        """
        if lambda_param <= 0:
            raise ValueError(f"lambda_param должна быть > 0, получено {lambda_param}")

        R = random.random()  # U(0, 1)
        # Избегаем ln(0), используя 1-R вместо R (эквивалентно)
        R = max(R, 1e-10)  # Гарантируем R > 0

        return -(1.0 / lambda_param) * math.log(R)

    # ========================================================================
    # РАСПРЕДЕЛЕНИЕ ВЕЙБУЛА
    # ========================================================================

    def generate_weibull(self, a: float, b: float) -> float:
        """
        Генерирует случайную величину из распределения Вейбула.

        Формула: x = -b * (ln(R))^(1/a)
        где R ~ U(0,1), a и b - параметры формы и масштаба

        Args:
            a: Параметр формы (shape parameter)
            b: Параметр масштаба (scale parameter)

        Returns:
            Случайная величина из распределения Вейбула

        Raises:
            ValueError: Если a <= 0 или b <= 0
        """
        if a <= 0:
            raise ValueError(f"Параметр a должен быть > 0, получено {a}")
        if b <= 0:
            raise ValueError(f"Параметр b должен быть > 0, получено {b}")

        R = random.random()  # U(0, 1)
        R = max(R, 1e-10)  # Гарантируем R > 0

        # x = -b * (ln(R))^(1/a) = b * (-ln(R))^(1/a)
        ln_R = math.log(R)
        return b * ((-ln_R) ** (1.0 / a))

    # ========================================================================
    # ГАММА-РАСПРЕДЕЛЕНИЕ
    # ========================================================================

    def generate_gamma(self, lambda_param: float, eta: int) -> float:
        """
        Генерирует случайную величину из Гамма-распределения.

        Формула: x = -(1/λ) * Σ ln(1 - R_j) для j = 1..η
        где R_j ~ U(0,1), λ - параметр, η - целое число (параметр формы)

        Args:
            lambda_param: Параметр λ (интенсивность)
            eta: Параметр η (целое число, определяет форму распределения)

        Returns:
            Случайная величина из Гамма-распределения

        Raises:
            ValueError: Если lambda_param <= 0 или eta <= 0
        """
        if lambda_param <= 0:
            raise ValueError(f"lambda_param должна быть > 0, получено {lambda_param}")
        if eta <= 0:
            raise ValueError(f"eta должна быть > 0, получено {eta}")

        # x = -(1/λ) * Σ ln(1 - R_j) для j = 1..η
        sum_ln = 0.0
        for _ in range(eta):
            R = random.random()  # U(0, 1)
            R = min(R, 1 - 1e-10)  # Гарантируем (1-R) > 0
            sum_ln += math.log(1.0 - R)

        return -(1.0 / lambda_param) * sum_ln

    # ========================================================================
    # НОРМАЛЬНОЕ (ГАУССОВСКОЕ) РАСПРЕДЕЛЕНИЕ
    # ========================================================================

    def generate_normal(self, m: float, sigma: float) -> float:
        """
        Генерирует случайную величину из нормального распределения.

        Формула: X = σ * √2 * (Σ R_i - 3) + m для i = 1..6
        где R_i ~ U(0,1), m - математическое ожидание, σ - стандартное отклонение

        Args:
            m: Математическое ожидание (mean)
            sigma: Стандартное отклонение (standard deviation)

        Returns:
            Случайная величина из нормального распределения N(m, σ²)

        Raises:
            ValueError: Если sigma <= 0
        """
        if sigma <= 0:
            raise ValueError(f"sigma должна быть > 0, получено {sigma}")

        # Генерируем 6 равномерно распределённых величин
        sum_R = sum(random.random() for _ in range(6))

        # X = σ * √2 * (Σ R_i - 3) + m
        sqrt_2 = math.sqrt(2.0)
        X = sigma * sqrt_2 * (sum_R - 3.0) + m

        return X

    # ========================================================================
    # УНИВЕРСАЛЬНЫЙ МЕТОД
    # ========================================================================

    def generate(self, dist_type: DistributionType, **kwargs) -> float:
        """
        Универсальный метод для генерации случайных величин любого типа.

        Args:
            dist_type: Тип распределения (из DistributionType)
            **kwargs: Параметры распределения в виде именованных аргументов:
                - Экспоненциальное: lambda_param=float
                - Вейбула: a=float, b=float
                - Гамма: lambda_param=float, eta=int
                - Нормальное: m=float, sigma=float

        Returns:
            Случайная величина из заданного распределения

        Raises:
            ValueError: Если распределение не поддерживается или параметры неверны
        """
        if dist_type == DistributionType.EXPONENTIAL:
            if 'lambda_param' not in kwargs:
                raise ValueError("Для EXPONENTIAL требуется параметр lambda_param")
            return self.generate_exponential(kwargs['lambda_param'])

        elif dist_type == DistributionType.WEIBULL:
            if 'a' not in kwargs or 'b' not in kwargs:
                raise ValueError("Для WEIBULL требуются параметры a и b")
            return self.generate_weibull(kwargs['a'], kwargs['b'])

        elif dist_type == DistributionType.GAMMA:
            if 'lambda_param' not in kwargs or 'eta' not in kwargs:
                raise ValueError("Для GAMMA требуются параметры lambda_param и eta")
            return self.generate_gamma(kwargs['lambda_param'], kwargs['eta'])

        elif dist_type == DistributionType.NORMAL:
            if 'm' not in kwargs or 'sigma' not in kwargs:
                raise ValueError("Для NORMAL требуются параметры m и sigma")
            return self.generate_normal(kwargs['m'], kwargs['sigma'])

        else:
            raise ValueError(f"Неизвестный тип распределения: {dist_type}")


# ============================================================================
# ТЕСТИРОВАНИЕ
# ============================================================================

if __name__ == '__main__':
    import statistics as stat

    print("=" * 70)
    print("ТЕСТИРОВАНИЕ ГЕНЕРАТОРА СЛУЧАЙНЫХ ВЕЛИЧИН")
    print("=" * 70)

    gen = RandomGenerator(seed=18)

    # Тест 1: Экспоненциальное распределение
    print("\n1. Экспоненциальное распределение (λ=0.4)")
    print("-" * 70)
    lambda_val = 0.4
    samples = [gen.generate_exponential(lambda_val) for _ in range(10000)]
    mean_empirical = stat.mean(samples)
    mean_theoretical = 1.0 / lambda_val
    print(f"   Теоретическое среднее: {mean_theoretical:.4f}")
    print(f"   Эмпирическое среднее:  {mean_empirical:.4f}")
    print(f"   Ошибка: {abs(mean_empirical - mean_theoretical):.4f}")

    # Тест 2: Распределение Вейбула
    print("\n2. Распределение Вейбула (a=2.0, b=2.5)")
    print("-" * 70)
    a, b = 2.0, 2.5
    samples = [gen.generate_weibull(a, b) for _ in range(10000)]
    mean_empirical = stat.mean(samples)
    # Для Вейбула: E[X] = b * Γ(1 + 1/a)
    mean_theoretical = b * math.gamma(1 + 1.0 / a)
    print(f"   Теоретическое среднее: {mean_theoretical:.4f}")
    print(f"   Эмпирическое среднее:  {mean_empirical:.4f}")
    print(f"   Ошибка: {abs(mean_empirical - mean_theoretical):.4f}")

    # Тест 3: Гамма-распределение
    print("\n3. Гамма-распределение (λ=0.4, η=2)")
    print("-" * 70)
    lambda_val, eta = 0.4, 2
    samples = [gen.generate_gamma(lambda_val, eta) for _ in range(10000)]
    mean_empirical = stat.mean(samples)
    mean_theoretical = eta / lambda_val  # E[X] = η/λ
    print(f"   Теоретическое среднее: {mean_theoretical:.4f}")
    print(f"   Эмпирическое среднее:  {mean_empirical:.4f}")
    print(f"   Ошибка: {abs(mean_empirical - mean_theoretical):.4f}")

    # Тест 4: Нормальное распределение
    print("\n4. Нормальное распределение (m=2.5, σ=0.5)")
    print("-" * 70)
    m, sigma = 2.5, 0.5
    samples = [gen.generate_normal(m, sigma) for _ in range(10000)]
    mean_empirical = stat.mean(samples)
    std_empirical = stat.stdev(samples)
    print(f"   Теоретическое среднее: {m:.4f}")
    print(f"   Эмпирическое среднее:  {mean_empirical:.4f}")
    print(f"   Ошибка среднего: {abs(mean_empirical - m):.4f}")
    print(f"   Теоретическое стд:    {sigma:.4f}")
    print(f"   Эмпирическое стд:     {std_empirical:.4f}")
    print(f"   Ошибка стд: {abs(std_empirical - sigma):.4f}")

    print("\n" + "=" * 70)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 70)
