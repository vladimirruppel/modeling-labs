"""
Классы систем массового обслуживания (СМО) для различных типов.
"""

from utils import convert_time_to_intensity, print_stability_warning
from formulas import (
    FormulasMMn0, FormulasMM1m, FormulasMM1inf,
    FormulasMMnm, FormulasMMninf,
    FormulasClosedSingle, FormulasClosedMulti
)
from calculations import check_stability_condition


class QueueingSystem:
    """
    Базовый класс для всех СМО.

    Параметры можно передать либо как интенсивности (lambda_val, mu_val),
    либо как средние времена (avg_arrival, avg_service).
    """

    def __init__(self, lambda_val=None, mu_val=None, avg_arrival=None, avg_service=None):
        """
        Args:
            lambda_val: интенсивность входящего потока (машин/час или заявок/мин)
            mu_val: интенсивность обслуживания одного канала
            avg_arrival: среднее время между приходами (в минутах)
            avg_service: среднее время обслуживания (в минутах)
        """
        # Преобразование времен в интенсивности
        if lambda_val is not None:
            self.lambda_ = lambda_val
        elif avg_arrival is not None:
            self.lambda_ = convert_time_to_intensity(avg_arrival)
        else:
            raise ValueError("Необходимо указать lambda_val или avg_arrival")

        if mu_val is not None:
            self.mu = mu_val
        elif avg_service is not None:
            self.mu = convert_time_to_intensity(avg_service)
        else:
            raise ValueError("Необходимо указать mu_val или avg_service")

        # Общие параметры
        self.rho = self.lambda_ / self.mu if self.mu > 0 else float('inf')

    def calculate_all_characteristics(self):
        """
        Вычисляет все характеристики системы.

        Должен быть переопределен в подклассах.
        """
        raise NotImplementedError("Подклассы должны реализовать этот метод")

    def get_system_name(self):
        """Возвращает название типа СМО"""
        raise NotImplementedError

    def validate(self):
        """Проверяет корректность параметров системы"""
        if self.lambda_ <= 0 or self.mu <= 0:
            raise ValueError("Интенсивности должны быть положительными")


class MMn0(QueueingSystem):
    """M|M|n|0 - многоканальная СМО с отказами (без очереди)"""

    def __init__(self, n_channels, **kwargs):
        """
        Args:
            n_channels: количество каналов (n)
            **kwargs: параметры базового класса (lambda_val, mu_val и т.д.)
        """
        super().__init__(**kwargs)
        self.n = n_channels
        self.formulas = FormulasMMn0(self.lambda_, self.mu, self.n)
        self.validate()

    def get_system_name(self):
        return f"M|M|{self.n}|0 (многоканальная с отказами)"

    def calculate_all_characteristics(self):
        """Вычисляет все характеристики для M|M|n|0"""
        p0 = self.formulas.calculate_p0()
        probabilities = self.formulas.calculate_probabilities()
        p_rejection = self.formulas.calculate_rejection_prob()
        q = self.formulas.calculate_relative_throughput()
        A = self.formulas.calculate_absolute_throughput()
        k_avg = self.formulas.calculate_avg_busy_channels()

        return {
            'type': 'MMn0',
            'n_channels': self.n,
            'lambda': self.lambda_,
            'mu': self.mu,
            'rho': self.rho,
            'p0': p0,
            'probabilities': probabilities,
            'p_rejection': p_rejection,
            'relative_throughput': q,
            'absolute_throughput': A,
            'avg_busy_channels': k_avg
        }


class MM1m(QueueingSystem):
    """M|M|1|m - одноканальная СМО с конечной очередью"""

    def __init__(self, m_queue, **kwargs):
        """
        Args:
            m_queue: максимальное количество мест в очереди
            **kwargs: параметры базового класса
        """
        super().__init__(**kwargs)
        self.m = m_queue
        self.formulas = FormulasMM1m(self.lambda_, self.mu, self.m)
        self.validate()

    def get_system_name(self):
        return f"M|M|1|{self.m} (одноканальная с конечной очередью)"

    def calculate_all_characteristics(self):
        """Вычисляет все характеристики для M|M|1|m"""
        p0 = self.formulas.calculate_p0()
        probabilities = self.formulas.calculate_probabilities()
        p_rejection = self.formulas.calculate_rejection_prob()
        q = self.formulas.calculate_relative_throughput()
        A = self.formulas.calculate_absolute_throughput()
        r_avg = self.formulas.calculate_avg_queue_length()
        t_wait = self.formulas.calculate_avg_wait_time()
        t_system = self.formulas.calculate_avg_system_time()

        return {
            'type': 'MM1m',
            'm_queue': self.m,
            'lambda': self.lambda_,
            'mu': self.mu,
            'rho': self.rho,
            'p0': p0,
            'probabilities': probabilities,
            'p_rejection': p_rejection,
            'relative_throughput': q,
            'absolute_throughput': A,
            'avg_queue_length': r_avg,
            'avg_wait_time': t_wait,
            'avg_system_time': t_system
        }


class MM1inf(QueueingSystem):
    """M|M|1|∞ - одноканальная СМО с бесконечной очередью"""

    def __init__(self, **kwargs):
        """
        Args:
            **kwargs: параметры базового класса
        """
        super().__init__(**kwargs)
        self.validate()

        # Проверка условия стабильности
        is_stable, rho, _ = check_stability_condition(self.lambda_, self.mu, 1)
        if not is_stable:
            raise ValueError(f"Система нестабильна: ρ = {rho:.4f} >= 1")

        self.formulas = FormulasMM1inf(self.lambda_, self.mu)

    def get_system_name(self):
        return "M|M|1|∞ (одноканальная с бесконечной очередью)"

    def calculate_all_characteristics(self):
        """Вычисляет все характеристики для M|M|1|∞"""
        p0 = self.formulas.calculate_p0()
        probabilities = self.formulas.calculate_probabilities()
        q = self.formulas.calculate_relative_throughput()
        A = self.formulas.calculate_absolute_throughput()
        r_avg = self.formulas.calculate_avg_queue_length()
        nu_avg = self.formulas.calculate_avg_system_length()
        t_wait = self.formulas.calculate_avg_wait_time()
        t_system = self.formulas.calculate_avg_system_time()

        return {
            'type': 'MM1inf',
            'lambda': self.lambda_,
            'mu': self.mu,
            'rho': self.rho,
            'p0': p0,
            'probabilities': probabilities,
            'relative_throughput': q,
            'absolute_throughput': A,
            'avg_queue_length': r_avg,
            'avg_system_length': nu_avg,
            'avg_wait_time': t_wait,
            'avg_system_time': t_system
        }


class MMnm(QueueingSystem):
    """M|M|n|m - многоканальная СМО с конечной очередью"""

    def __init__(self, n_channels, m_queue, **kwargs):
        """
        Args:
            n_channels: количество каналов
            m_queue: максимальное количество мест в очереди
            **kwargs: параметры базового класса
        """
        super().__init__(**kwargs)
        self.n = n_channels
        self.m = m_queue
        self.formulas = FormulasMMnm(self.lambda_, self.mu, self.n, self.m)
        self.validate()

    def get_system_name(self):
        return f"M|M|{self.n}|{self.m} (многоканальная с конечной очередью)"

    def calculate_all_characteristics(self):
        """Вычисляет все характеристики для M|M|n|m"""
        p0 = self.formulas.calculate_p0()
        probabilities = self.formulas.calculate_probabilities()
        p_rejection = self.formulas.calculate_rejection_prob()
        q = self.formulas.calculate_relative_throughput()
        A = self.formulas.calculate_absolute_throughput()
        r_avg = self.formulas.calculate_avg_queue_length()
        t_wait = self.formulas.calculate_avg_wait_time()

        return {
            'type': 'MMnm',
            'n_channels': self.n,
            'm_queue': self.m,
            'lambda': self.lambda_,
            'mu': self.mu,
            'rho': self.rho,
            'p0': p0,
            'probabilities': probabilities,
            'p_rejection': p_rejection,
            'relative_throughput': q,
            'absolute_throughput': A,
            'avg_queue_length': r_avg,
            'avg_wait_time': t_wait
        }


class MMninf(QueueingSystem):
    """M|M|n|∞ - многоканальная СМО с бесконечной очередью"""

    def __init__(self, n_channels, **kwargs):
        """
        Args:
            n_channels: количество каналов
            **kwargs: параметры базового класса
        """
        super().__init__(**kwargs)
        self.n = n_channels
        self.validate()

        # Проверка условия стабильности
        is_stable, rho, condition = check_stability_condition(self.lambda_, self.mu, self.n)
        if not is_stable:
            raise ValueError(f"Система нестабильна: ρ/n = {condition:.4f} >= 1")

        self.formulas = FormulasMMninf(self.lambda_, self.mu, self.n)

    def get_system_name(self):
        return f"M|M|{self.n}|∞ (многоканальная с бесконечной очередью)"

    def calculate_all_characteristics(self):
        """Вычисляет все характеристики для M|M|n|∞"""
        p0 = self.formulas.calculate_p0()
        probabilities = self.formulas.calculate_probabilities()
        q = self.formulas.calculate_relative_throughput()
        A = self.formulas.calculate_absolute_throughput()
        r_avg = self.formulas.calculate_avg_queue_length()
        nu_avg = self.formulas.calculate_avg_system_length()
        t_wait = self.formulas.calculate_avg_wait_time()
        t_system = self.formulas.calculate_avg_system_time()

        return {
            'type': 'MMninf',
            'n_channels': self.n,
            'lambda': self.lambda_,
            'mu': self.mu,
            'rho': self.rho,
            'p0': p0,
            'probabilities': probabilities,
            'relative_throughput': q,
            'absolute_throughput': A,
            'avg_queue_length': r_avg,
            'avg_system_length': nu_avg,
            'avg_wait_time': t_wait,
            'avg_system_time': t_system
        }


class ClosedSingle(QueueingSystem):
    """Замкнутая одноканальная СМО"""

    def __init__(self, N_sources, **kwargs):
        """
        Args:
            N_sources: количество источников заявок
            **kwargs: параметры базового класса
        """
        super().__init__(**kwargs)
        self.N = N_sources
        self.formulas = FormulasClosedSingle(self.N, self.lambda_, self.mu)
        self.validate()

    def get_system_name(self):
        return f"Замкнутая одноканальная СМО (N={self.N} источников)"

    def calculate_all_characteristics(self):
        """Вычисляет все характеристики для замкнутой одноканальной СМО"""
        p0 = self.formulas.calculate_p0()
        probabilities = self.formulas.calculate_probabilities()
        nu_avg = self.formulas.calculate_avg_system_length()
        r_avg = self.formulas.calculate_avg_queue_length()
        lambda_eff = self.formulas.calculate_effective_lambda()
        t_wait = self.formulas.calculate_avg_wait_time()
        t_system = self.formulas.calculate_avg_system_time()

        return {
            'type': 'ClosedSingle',
            'N_sources': self.N,
            'lambda': self.lambda_,
            'mu': self.mu,
            'p0': p0,
            'probabilities': probabilities,
            'avg_system_length': nu_avg,
            'avg_queue_length': r_avg,
            'effective_lambda': lambda_eff,
            'avg_wait_time': t_wait,
            'avg_system_time': t_system
        }


class ClosedMulti(QueueingSystem):
    """Замкнутая многоканальная СМО"""

    def __init__(self, N_sources, n_channels, **kwargs):
        """
        Args:
            N_sources: количество источников заявок
            n_channels: количество каналов обслуживания
            **kwargs: параметры базового класса
        """
        super().__init__(**kwargs)
        self.N = N_sources
        self.n = n_channels
        self.formulas = FormulasClosedMulti(self.N, self.n, self.lambda_, self.mu)
        self.validate()

    def get_system_name(self):
        return f"Замкнутая многоканальная СМО (N={self.N} источников, n={self.n} каналов)"

    def calculate_all_characteristics(self):
        """Вычисляет все характеристики для замкнутой многоканальной СМО"""
        p0 = self.formulas.calculate_p0()
        probabilities = self.formulas.calculate_probabilities()
        nu_avg = self.formulas.calculate_avg_system_length()
        r_avg = self.formulas.calculate_avg_queue_length()
        lambda_eff = self.formulas.calculate_effective_lambda()
        t_wait = self.formulas.calculate_avg_wait_time()
        t_system = self.formulas.calculate_avg_system_time()

        return {
            'type': 'ClosedMulti',
            'N_sources': self.N,
            'n_channels': self.n,
            'lambda': self.lambda_,
            'mu': self.mu,
            'p0': p0,
            'probabilities': probabilities,
            'avg_system_length': nu_avg,
            'avg_queue_length': r_avg,
            'effective_lambda': lambda_eff,
            'avg_wait_time': t_wait,
            'avg_system_time': t_system
        }
