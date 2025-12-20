"""
Классы для расчета характеристик различных типов марковских СМО.
"""

import math
from calculations import (
    calculate_erlang_b, calculate_erlang_c, calculate_geometric_sum,
    calculate_power, calculate_factorial
)


class BaseFormulas:
    """Базовый класс для формул всех типов СМО"""

    def __init__(self, lambda_val, mu):
        """
        Args:
            lambda_val: интенсивность входящего потока
            mu: интенсивность обслуживания одного канала
        """
        self.lambda_ = lambda_val
        self.mu = mu
        self.rho = lambda_val / mu if mu > 0 else float('inf')


class FormulasMMn0(BaseFormulas):
    """
    Формулы для M|M|n|0 - многоканальная СМО с отказами (без очереди).

    Формулы Эрланга:
    - P₀ = [1 + ρ/1! + ρ²/2! + ... + ρⁿ/n!]⁻¹
    - Pₖ = (ρᵏ/k!) · P₀ для k = 1,2,...,n
    - P_отк = Pₙ = (ρⁿ/n!) · P₀
    - q = 1 - P_отк
    - A = λ · q
    """

    def __init__(self, lambda_val, mu, n_channels):
        """
        Args:
            lambda_val: интенсивность входящего потока
            mu: интенсивность обслуживания одного канала
            n_channels: количество каналов (n)
        """
        super().__init__(lambda_val, mu)
        self.n = n_channels

    def calculate_p0(self):
        """
        Вычисляет вероятность того, что система свободна (P₀).

        Формула: P₀ = [1 + ρ/1! + ρ²/2! + ... + ρⁿ/n!]⁻¹
        """
        sum_val = 0.0
        for k in range(self.n + 1):
            term = calculate_power(self.rho, k) / calculate_factorial(k)
            sum_val += term

        if sum_val == 0:
            return 0.0

        return 1.0 / sum_val

    def calculate_probabilities(self):
        """
        Вычисляет все вероятности состояний P₀, P₁, ..., Pₙ.

        Формула: Pₖ = (ρᵏ/k!) · P₀
        """
        p0 = self.calculate_p0()
        probabilities = {0: p0}

        for k in range(1, self.n + 1):
            pk = (calculate_power(self.rho, k) / calculate_factorial(k)) * p0
            probabilities[k] = pk

        return probabilities

    def calculate_rejection_prob(self):
        """
        Вычисляет вероятность отказа (потери заявки).

        Формула: P_отк = Pₙ = (ρⁿ/n!) · P₀
        """
        p0 = self.calculate_p0()
        return (calculate_power(self.rho, self.n) / calculate_factorial(self.n)) * p0

    def calculate_relative_throughput(self):
        """
        Вычисляет относительную пропускную способность.

        Формула: q = 1 - P_отк
        """
        return 1.0 - self.calculate_rejection_prob()

    def calculate_absolute_throughput(self):
        """
        Вычисляет абсолютную пропускную способность.

        Формула: A = λ · q
        """
        return self.lambda_ * self.calculate_relative_throughput()

    def calculate_avg_busy_channels(self):
        """
        Вычисляет среднее количество занятых каналов.

        Формула: k̄ = A/μ = ρ(1 - Pₙ)
        """
        return self.rho * (1.0 - self.calculate_rejection_prob())


class FormulasMM1m(BaseFormulas):
    """
    Формулы для M|M|1|m - одноканальная СМО с конечной очередью.

    Параметры:
    - m: максимальное количество мест в очереди (размер буфера = m+1)
    """

    def __init__(self, lambda_val, mu, m_queue):
        """
        Args:
            lambda_val: интенсивность входящего потока
            mu: интенсивность обслуживания
            m_queue: максимальное количество мест в очереди
        """
        super().__init__(lambda_val, mu)
        self.m = m_queue

    def calculate_p0(self):
        """
        Вычисляет вероятность того, что система свободна (P₀).

        Формула: P₀ = (1-ρ)/(1-ρᵐ⁺²) при ρ ≠ 1
        P₀ = 1/(m+2) при ρ = 1
        """
        if abs(self.rho - 1.0) < 1e-10:  # ρ ≈ 1
            return 1.0 / (self.m + 2)
        else:
            numerator = 1.0 - self.rho
            denominator = 1.0 - calculate_power(self.rho, self.m + 2)
            if denominator == 0:
                return 0.0
            return numerator / denominator

    def calculate_probabilities(self):
        """
        Вычисляет все вероятности состояний P₀, P₁, ..., P_{m+1}.

        Формула: Pₖ = ρᵏ · P₀
        """
        p0 = self.calculate_p0()
        probabilities = {0: p0}

        for k in range(1, self.m + 2):
            pk = calculate_power(self.rho, k) * p0
            probabilities[k] = pk

        return probabilities

    def calculate_rejection_prob(self):
        """
        Вычисляет вероятность отказа (потери заявки).

        Формула: P_отк = P_{m+1} = ρᵐ⁺¹ · P₀
        """
        p0 = self.calculate_p0()
        return calculate_power(self.rho, self.m + 1) * p0

    def calculate_relative_throughput(self):
        """
        Вычисляет относительную пропускную способность.

        Формула: q = 1 - P_отк
        """
        return 1.0 - self.calculate_rejection_prob()

    def calculate_absolute_throughput(self):
        """
        Вычисляет абсолютную пропускную способность.

        Формула: A = λ · q
        """
        return self.lambda_ * self.calculate_relative_throughput()

    def calculate_avg_queue_length(self):
        """
        Вычисляет среднюю длину очереди.

        Формула: r̄ = ρ²(1-ρᵐ(m+1-mρ))/(1-ρᵐ⁺²)(1-ρ)²
        """
        if abs(self.rho - 1.0) < 1e-10:  # ρ ≈ 1
            return self.m * (self.m + 1) / 2

        numerator = (
            self.rho ** 2 *
            (1.0 - calculate_power(self.rho, self.m) * (self.m + 1 - self.m * self.rho))
        )
        denominator = (1.0 - calculate_power(self.rho, self.m + 2)) * (1.0 - self.rho) ** 2

        if denominator == 0:
            return 0.0

        return numerator / denominator

    def calculate_avg_wait_time(self):
        """
        Вычисляет среднее время ожидания в очереди.

        Формула: t̄_ож = r̄/λ_эфф, где λ_эфф = λ(1 - P_{m+1})
        """
        r_bar = self.calculate_avg_queue_length()
        lambda_eff = self.lambda_ * self.calculate_relative_throughput()

        if lambda_eff == 0:
            return 0.0

        return r_bar / lambda_eff

    def calculate_avg_system_time(self):
        """
        Вычисляет среднее время пребывания в системе.

        Формула: t̄_сист = t̄_ож + 1/μ
        """
        t_wait = self.calculate_avg_wait_time()
        return t_wait + 1.0 / self.mu


class FormulasMM1inf(BaseFormulas):
    """
    Формулы для M|M|1|∞ - одноканальная СМО с бесконечной очередью.

    Условие применимости: ρ < 1
    """

    def __init__(self, lambda_val, mu):
        """
        Args:
            lambda_val: интенсивность входящего потока
            mu: интенсивность обслуживания
        """
        super().__init__(lambda_val, mu)

        if self.rho >= 1:
            raise ValueError(f"Система нестабильна: ρ = {self.rho:.4f} >= 1")

    def calculate_p0(self):
        """
        Вычисляет вероятность того, что система свободна (P₀).

        Формула: P₀ = 1 - ρ
        """
        return 1.0 - self.rho

    def calculate_probabilities(self):
        """
        Вычисляет все вероятности состояний P₀, P₁, P₂, ...

        Формула: Pₖ = ρᵏ(1-ρ)
        """
        p0 = self.calculate_p0()
        # Возвращаем первые 50 состояний
        probabilities = {}
        for k in range(50):
            pk = calculate_power(self.rho, k) * p0
            if pk < 1e-10:
                break
            probabilities[k] = pk

        return probabilities

    def calculate_rejection_prob(self):
        """
        Вероятность отказа (для бесконечной очереди).

        Формула: P_отк = 0 (отказов нет)
        """
        return 0.0

    def calculate_relative_throughput(self):
        """
        Вычисляет относительную пропускную способность.

        Формула: q = 1 (все заявки обслуживаются)
        """
        return 1.0

    def calculate_absolute_throughput(self):
        """
        Вычисляет абсолютную пропускную способность.

        Формула: A = λ
        """
        return self.lambda_

    def calculate_avg_queue_length(self):
        """
        Вычисляет среднюю длину очереди.

        Формула: r̄ = ρ²/(1-ρ)
        """
        return self.rho ** 2 / (1.0 - self.rho)

    def calculate_avg_system_length(self):
        """
        Вычисляет среднее количество заявок в системе (в обслуживании + в очереди).

        Формула: ν̄ = ρ/(1-ρ)
        """
        return self.rho / (1.0 - self.rho)

    def calculate_avg_wait_time(self):
        """
        Вычисляет среднее время ожидания в очереди.

        Формула: t̄_ож = ρ/(λ(1-ρ))
        """
        if self.lambda_ == 0:
            return 0.0
        return self.rho / (self.lambda_ * (1.0 - self.rho))

    def calculate_avg_system_time(self):
        """
        Вычисляет среднее время пребывания в системе.

        Формула: t̄_сист = 1/(μ(1-ρ))
        """
        return 1.0 / (self.mu * (1.0 - self.rho))


class FormulasMMnm(BaseFormulas):
    """
    Формулы для M|M|n|m - многоканальная СМО с конечной очередью.

    Параметры:
    - n: количество каналов обслуживания
    - m: максимальное количество мест в очереди
    """

    def __init__(self, lambda_val, mu, n_channels, m_queue):
        """
        Args:
            lambda_val: интенсивность входящего потока
            mu: интенсивность обслуживания одного канала
            n_channels: количество каналов
            m_queue: максимальное количество мест в очереди
        """
        super().__init__(lambda_val, mu)
        self.n = n_channels
        self.m = m_queue

    def calculate_p0(self):
        """
        Вычисляет вероятность того, что система свободна (P₀).

        Для k ≤ n: Pₖ = (ρⁿ/k!) / P₀
        Для k > n: Pₖ = (ρᵏ/nⁿ⁻ᵏ·k!) / P₀

        P₀ получается из условия Σ Pₖ = 1
        """
        sum_val = 0.0

        # Сумма для k ≤ n
        for k in range(self.n):
            term = calculate_power(self.rho, k) / calculate_factorial(k)
            sum_val += term

        # Сумма для k > n (элементы в очереди)
        for k in range(self.n, self.n + self.m + 1):
            term = (calculate_power(self.rho, k) /
                   (calculate_factorial(self.n) * calculate_power(self.n, k - self.n)))
            sum_val += term

        if sum_val == 0:
            return 0.0

        return 1.0 / sum_val

    def calculate_probabilities(self):
        """
        Вычисляет все вероятности состояний P₀, P₁, ..., P_{n+m}.
        """
        p0 = self.calculate_p0()
        probabilities = {0: p0}

        # Вероятности для k ≤ n (все каналы занятостью)
        for k in range(1, self.n):
            pk = (calculate_power(self.rho, k) / calculate_factorial(k)) * p0
            probabilities[k] = pk

        # Вероятности для k > n (есть очередь)
        for k in range(self.n, self.n + self.m + 1):
            pk = (calculate_power(self.rho, k) /
                 (calculate_factorial(self.n) * calculate_power(self.n, k - self.n))) * p0
            probabilities[k] = pk

        return probabilities

    def calculate_rejection_prob(self):
        """
        Вычисляет вероятность отказа (потери заявки).

        Формула: P_отк = P_{n+m}
        """
        p0 = self.calculate_p0()
        return (calculate_power(self.rho, self.n + self.m) /
               (calculate_factorial(self.n) * calculate_power(self.n, self.m))) * p0

    def calculate_relative_throughput(self):
        """
        Вычисляет относительную пропускную способность.

        Формула: q = 1 - P_отк
        """
        return 1.0 - self.calculate_rejection_prob()

    def calculate_absolute_throughput(self):
        """
        Вычисляет абсолютную пропускную способность.

        Формула: A = λ · q
        """
        return self.lambda_ * self.calculate_relative_throughput()

    def calculate_avg_queue_length(self):
        """
        Вычисляет среднюю длину очереди.
        """
        p0 = self.calculate_p0()
        sum_val = 0.0

        for j in range(1, self.m + 1):
            k = self.n + j
            prob_k = (calculate_power(self.rho, k) /
                     (calculate_factorial(self.n) * calculate_power(self.n, j))) * p0
            sum_val += j * prob_k

        return sum_val

    def calculate_avg_wait_time(self):
        """
        Вычисляет среднее время ожидания в очереди.

        Формула: t̄_ож = r̄/λ_эфф
        """
        r_bar = self.calculate_avg_queue_length()
        lambda_eff = self.lambda_ * self.calculate_relative_throughput()

        if lambda_eff == 0:
            return 0.0

        return r_bar / lambda_eff


class FormulasMMninf(BaseFormulas):
    """
    Формулы для M|M|n|∞ - многоканальная СМО с бесконечной очередью.

    Условие применимости: ρ/n < 1, где ρ = λ/μ
    """

    def __init__(self, lambda_val, mu, n_channels):
        """
        Args:
            lambda_val: интенсивность входящего потока
            mu: интенсивность обслуживания одного канала
            n_channels: количество каналов
        """
        super().__init__(lambda_val, mu)
        self.n = n_channels

        condition = self.rho / self.n
        if condition >= 1:
            raise ValueError(f"Система нестабильна: ρ/n = {condition:.4f} >= 1")

    def calculate_p0(self):
        """
        Вычисляет вероятность того, что система свободна (P₀).

        Использует формулу Эрланга C
        """
        sum_val = 0.0

        # Сумма для k < n
        for k in range(self.n):
            term = calculate_power(self.rho, k) / calculate_factorial(k)
            sum_val += term

        # Сумма для k ≥ n
        erlang_coeff = calculate_power(self.rho, self.n) / calculate_factorial(self.n)
        erlang_sum = erlang_coeff / (1.0 - self.rho / self.n)
        sum_val += erlang_sum

        if sum_val == 0:
            return 0.0

        return 1.0 / sum_val

    def calculate_probabilities(self):
        """
        Вычисляет все вероятности состояний P₀, P₁, P₂, ...
        """
        p0 = self.calculate_p0()
        probabilities = {0: p0}

        # Вероятности для k < n
        for k in range(1, self.n):
            pk = (calculate_power(self.rho, k) / calculate_factorial(k)) * p0
            probabilities[k] = pk

        # Вероятности для k ≥ n (первые 50 состояний)
        for k in range(self.n, self.n + 50):
            pk = (calculate_power(self.rho, k) /
                 (calculate_factorial(self.n) * calculate_power(self.n, k - self.n))) * p0
            if pk < 1e-10:
                break
            probabilities[k] = pk

        return probabilities

    def calculate_rejection_prob(self):
        """
        Вероятность отказа (для бесконечной очереди).

        Формула: P_отк = 0
        """
        return 0.0

    def calculate_relative_throughput(self):
        """
        Вычисляет относительную пропускную способность.

        Формула: q = 1
        """
        return 1.0

    def calculate_absolute_throughput(self):
        """
        Вычисляет абсолютную пропускную способность.

        Формула: A = λ
        """
        return self.lambda_

    def calculate_avg_queue_length(self):
        """
        Вычисляет среднюю длину очереди.

        Использует формулу Эрланга C
        """
        erlang_c = calculate_erlang_c(self.rho, self.n)
        condition = self.rho / self.n
        return erlang_c * self.rho / (self.n * (1.0 - condition))

    def calculate_avg_system_length(self):
        """
        Вычисляет среднее количество заявок в системе.

        ν̄ = Σ k·Pₖ
        """
        probabilities = self.calculate_probabilities()
        sum_val = sum(k * pk for k, pk in probabilities.items())
        return sum_val

    def calculate_avg_wait_time(self):
        """
        Вычисляет среднее время ожидания в очереди.

        Формула: t̄_ож = r̄/λ
        """
        r_bar = self.calculate_avg_queue_length()
        if self.lambda_ == 0:
            return 0.0
        return r_bar / self.lambda_

    def calculate_avg_system_time(self):
        """
        Вычисляет среднее время пребывания в системе.

        Формула: t̄_сист = ν̄/λ
        """
        nu_bar = self.calculate_avg_system_length()
        if self.lambda_ == 0:
            return 0.0
        return nu_bar / self.lambda_


class FormulasClosedSingle(BaseFormulas):
    """
    Формулы для замкнутой одноканальной СМО.

    Параметры:
    - N: количество источников заявок
    - lambda_single: интенсивность источника (когда источник не ждет)
    - mu: интенсивность обслуживания
    """

    def __init__(self, N, lambda_single, mu):
        """
        Args:
            N: количество источников заявок
            lambda_single: интенсивность одного источника
            mu: интенсивность обслуживания
        """
        super().__init__(lambda_single, mu)
        self.N = N  # Общее количество источников

    def calculate_p0(self):
        """
        Вычисляет вероятность того, что система свободна (все источники ждут).

        Формула использует биномиальные коэффициенты
        """
        sum_val = 0.0
        rho = self.lambda_ / self.mu

        for k in range(self.N + 1):
            from math import comb
            binom = comb(self.N, k)
            term = binom * calculate_power(rho, k)
            sum_val += term

        if sum_val == 0:
            return 0.0

        return 1.0 / sum_val

    def calculate_probabilities(self):
        """
        Вычисляет вероятности всех состояний P₀, P₁, ..., Pₙ.

        Формула: Pₖ = C(N,k) * ρᵏ * P₀
        """
        p0 = self.calculate_p0()
        probabilities = {0: p0}
        rho = self.lambda_ / self.mu

        from math import comb
        for k in range(1, self.N + 1):
            binom = comb(self.N, k)
            pk = binom * calculate_power(rho, k) * p0
            probabilities[k] = pk

        return probabilities

    def calculate_avg_system_length(self):
        """
        Вычисляет среднее количество заявок в системе.

        ν̄ = Σ k·Pₖ
        """
        probabilities = self.calculate_probabilities()
        return sum(k * pk for k, pk in probabilities.items())

    def calculate_avg_queue_length(self):
        """
        Вычисляет среднюю длину очереди (заявки в ожидании).

        r̄ = ν̄ - (1 - P₀)
        """
        nu_bar = self.calculate_avg_system_length()
        return nu_bar - (1.0 - self.calculate_p0())

    def calculate_effective_lambda(self):
        """
        Вычисляет эффективную интенсивность входящего потока.

        Формула: Λ̄ = (N - ν̄) * λ₀
        """
        nu_bar = self.calculate_avg_system_length()
        return (self.N - nu_bar) * self.lambda_

    def calculate_avg_wait_time(self):
        """
        Вычисляет среднее время ожидания в очереди.

        Формула: t̄_ож = r̄ / Λ̄
        """
        r_bar = self.calculate_avg_queue_length()
        lambda_eff = self.calculate_effective_lambda()

        if lambda_eff == 0:
            return 0.0

        return r_bar / lambda_eff

    def calculate_avg_system_time(self):
        """
        Вычисляет среднее время пребывания в системе.

        Формула: t̄_сист = (r̄ + 1) / Λ̄
        """
        r_bar = self.calculate_avg_queue_length()
        lambda_eff = self.calculate_effective_lambda()

        if lambda_eff == 0:
            return 0.0

        return (r_bar + 1.0) / lambda_eff


class FormulasClosedMulti(BaseFormulas):
    """
    Формулы для замкнутой многоканальной СМО.

    Параметры:
    - N: количество источников заявок
    - n: количество каналов обслуживания
    - lambda_single: интенсивность источника
    - mu: интенсивность обслуживания одного канала
    """

    def __init__(self, N, n_channels, lambda_single, mu):
        """
        Args:
            N: количество источников заявок
            n_channels: количество каналов обслуживания
            lambda_single: интенсивность одного источника
            mu: интенсивность обслуживания одного канала
        """
        super().__init__(lambda_single, mu)
        self.N = N  # Общее количество источников
        self.n = n_channels

    def calculate_p0(self):
        """
        Вычисляет вероятность того, что система свободна.

        Для замкнутой СМО используется сложная формула через биномиальные коэффициенты
        """
        from math import comb
        sum_val = 0.0
        rho = self.lambda_ / self.mu

        # Сумма для k от 0 до n
        for k in range(min(self.n + 1, self.N + 1)):
            binom = comb(self.N, k)
            # Произведение: ρ * (ρ+1) * ... * (ρ+k-1) / k!
            numerator = 1.0
            for j in range(k):
                numerator *= (self.rho + j)

            term = binom * numerator

            # Если k > n, добавляем множители для занятых каналов
            if k <= self.n:
                term = binom * calculate_power(rho, k)

            sum_val += term

        # Сумма для k от n+1 до N
        for k in range(self.n + 1, self.N + 1):
            binom = comb(self.N, k)
            # Произведение с повторяющимися множителями для n каналов
            term = binom * calculate_power(rho, k) / (calculate_power(self.n, k - self.n))
            sum_val += term

        if sum_val == 0:
            return 0.0

        return 1.0 / sum_val

    def calculate_probabilities(self):
        """
        Вычисляет вероятности всех состояний для многоканальной замкнутой СМО.
        """
        p0 = self.calculate_p0()
        probabilities = {0: p0}

        from math import comb

        # Вероятности для k от 1 до N
        for k in range(1, self.N + 1):
            binom = comb(self.N, k)

            if k <= self.n:
                # Все каналы заняты, очереди нет
                pk = binom * calculate_power(self.rho, k) * p0
            else:
                # Есть очередь
                pk = (binom * calculate_power(self.rho, k) /
                     calculate_power(self.n, k - self.n) * p0)

            probabilities[k] = pk

        return probabilities

    def calculate_avg_system_length(self):
        """
        Вычисляет среднее количество заявок в системе.
        """
        probabilities = self.calculate_probabilities()
        return sum(k * pk for k, pk in probabilities.items())

    def calculate_effective_lambda(self):
        """
        Вычисляет эффективную интенсивность входящего потока.

        Формула: Λ̄ = (N - ν̄) * λ₀
        """
        nu_bar = self.calculate_avg_system_length()
        return (self.N - nu_bar) * self.lambda_

    def calculate_avg_queue_length(self):
        """
        Вычисляет среднюю длину очереди.
        """
        probabilities = self.calculate_probabilities()
        sum_val = 0.0

        for k in range(self.n + 1, self.N + 1):
            sum_val += (k - self.n) * probabilities.get(k, 0)

        return sum_val

    def calculate_avg_wait_time(self):
        """
        Вычисляет среднее время ожидания в очереди.
        """
        r_bar = self.calculate_avg_queue_length()
        lambda_eff = self.calculate_effective_lambda()

        if lambda_eff == 0:
            return 0.0

        return r_bar / lambda_eff

    def calculate_avg_system_time(self):
        """
        Вычисляет среднее время пребывания в системе.
        """
        nu_bar = self.calculate_avg_system_length()
        lambda_eff = self.calculate_effective_lambda()

        if lambda_eff == 0:
            return 0.0

        return nu_bar / lambda_eff
