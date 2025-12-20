# -*- coding: utf-8 -*-
"""
ЛР №8: Моделирование немарковских СМО методом Монте-Карло.

Интерактивная программа для анализа систем массового обслуживания
с различными распределениями вероятности.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

from simulation_engine import SimulationEngine
from stats_aggregation import RealizationStatistics, MultiRealizationStatistics
from validation import MarkovianQueueTheory, validate_simulation, compare_configurations
from visualization import (
    plot_state_probabilities_comparison,
    plot_time_distributions,
    plot_configuration_comparison,
    ensure_output_dir
)
from config import DistributionType
from utils import (
    print_section_header,
    print_subsection_header,
    print_separator,
    print_results_table,
    print_probabilities_table,
    print_comparison_table,
    input_menu_choice,
    input_distribution_choice,
    input_distribution_params,
    input_integer,
    input_float,
    load_variant18_config,
    load_configuration,
    save_results,
    display_progress,
    format_value
)


class Lab8Application:
    """Главное приложение для ЛР №8."""

    def __init__(self):
        """Инициализация приложения."""
        self.config = load_variant18_config()
        self.last_results = None
        self.simulation_settings = {
            'T': 10000,
            'N_realizations': 100,
            'epsilon': 0.01,
            'seed': 18
        }

    def print_main_menu(self) -> Optional[int]:
        """Печать главного меню."""
        print_section_header("ЛР 8: Моделирование немарковских СМО (Монте-Карло)")

        options = {
            1: "Быстрый старт: Вариант 18 конфигурация 1",
            2: "Полный анализ: Все 3 конфигурации варианта 18",
            3: "Настраиваемое моделирование",
            4: "Сравнение распределений",
            5: "Анализ сходимости (оптимальное N)",
            6: "Валидация с теоретическими результатами",
            7: "Просмотр графиков",
            8: "Настройки симуляции",
            9: "Выход"
        }

        return input_menu_choice(options, "Главное меню")

    def handle_quick_start(self) -> None:
        """Опция 1: Быстрый старт."""
        print_section_header("Быстрый старт: Конфигурация 1 (M/M/1)")

        config = load_configuration(1)
        if not config:
            print("❌ Ошибка загрузки конфигурации")
            return

        print(f"\nПараметры системы:")
        print(f"  {config['description']}")
        print(f"  λ = {self.config['lambda']} машин/мин")
        print(f"  μ = {config['mu']} машин/мин")
        print(f"  T = {self.simulation_settings['T']} мин")
        print(f"  N = {self.simulation_settings['N_realizations']} реализаций")

        print("\nЗапуск симуляции...")

        engine = SimulationEngine(
            n_channels=config['n_channels'],
            m_queue=None,
            lambda_param=self.config['lambda'],
            mu_param=config['mu'],
            arrival_dist=DistributionType.EXPONENTIAL,
            service_dist=DistributionType.EXPONENTIAL,
            seed=self.simulation_settings['seed']
        )

        realizations = []
        for i in range(self.simulation_settings['N_realizations']):
            display_progress(i + 1, self.simulation_settings['N_realizations'], "Прогресс")
            result = engine.run_single_realization(self.simulation_settings['T'])
            real_stats = RealizationStatistics.from_simulation_result(result)
            realizations.append(real_stats)

        multi_stats = MultiRealizationStatistics(
            N_realizations=self.simulation_settings['N_realizations'],
            realizations=realizations
        )
        multi_stats.compute_statistics()

        self.last_results = multi_stats

        # Вывести результаты
        print_subsection_header("Результаты симуляции")

        print(f"\nОсновные характеристики:")
        print(f"  λ̄ = {multi_stats.avg_lambda:.6f} ± {multi_stats.std_lambda:.6f}")
        print(f"  μ̄ = {multi_stats.avg_mu:.6f} ± {multi_stats.std_mu:.6f}")
        print(f"  r̄ = {multi_stats.avg_queue_length:.6f} ± {multi_stats.std_queue_length:.6f}")
        print(f"  t̄_ож = {multi_stats.avg_wait_time:.6f} ± {multi_stats.std_wait_time:.6f} мин")
        print(f"  t̄_сист = {multi_stats.avg_system_time:.6f} ± {multi_stats.std_system_time:.6f} мин")
        print(f"  A = {multi_stats.avg_absolute_throughput:.6f}")

        # Сравнение с теорией
        print_subsection_header("Валидация (сравнение с теорией)")

        theory = MarkovianQueueTheory.calculate_mm1_characteristics(
            self.config['lambda'],
            config['mu']
        )

        if theory['stable']:
            validation = validate_simulation(multi_stats, theory, self.simulation_settings['epsilon'])

            print(f"\nМаксимальная ошибка: {validation.max_error:.6f} ({validation.max_error*100:.2f}%)")
            print(f"В допуске (ε={self.simulation_settings['epsilon']}): "
                  f"{'✓ ДА' if validation.within_tolerance else '✗ НЕТ'}")

            print(f"\nСравнение характеристик:")
            for name, comp in validation.characteristics_comparison.items():
                print(f"  {name}:")
                print(f"    Теория:     {comp['theoretical']:.6f}")
                print(f"    Симуляция:  {comp['simulated']:.6f}")
                print(f"    Ошибка:     {comp['error_pct']:.2f}%")

    def handle_full_variant18_analysis(self) -> None:
        """Опция 2: Полный анализ всех 3 конфигураций."""
        print_section_header("Полный анализ варианта 18")

        if not self.config or not self.config.get('configurations'):
            print("❌ Конфигурация варианта 18 не загружена")
            return

        print(f"\nБудет проанализировано {len(self.config['configurations'])} конфигураций")
        print(f"Параметры: T = {self.simulation_settings['T']}, "
              f"N = {self.simulation_settings['N_realizations']}\n")

        all_results = []
        comparison_configs = []

        for cfg in self.config['configurations']:
            print(f"\nОбработка: {cfg['description']}")
            print("-" * 70)

            engine = SimulationEngine(
                n_channels=cfg['n_channels'],
                m_queue=None,
                lambda_param=self.config['lambda'],
                mu_param=cfg['mu'],
                arrival_dist=DistributionType.EXPONENTIAL,
                service_dist=DistributionType.EXPONENTIAL,
                seed=self.simulation_settings['seed']
            )

            realizations = []
            for i in range(self.simulation_settings['N_realizations']):
                display_progress(i + 1, self.simulation_settings['N_realizations'])
                result = engine.run_single_realization(self.simulation_settings['T'])
                real_stats = RealizationStatistics.from_simulation_result(result)
                realizations.append(real_stats)

            multi_stats = MultiRealizationStatistics(
                N_realizations=self.simulation_settings['N_realizations'],
                realizations=realizations
            )
            multi_stats.compute_statistics()

            # Валидация
            if cfg['n_channels'] == 1:
                theory = MarkovianQueueTheory.calculate_mm1_characteristics(
                    self.config['lambda'],
                    cfg['mu']
                )
            else:
                theory = MarkovianQueueTheory.calculate_mmn_characteristics(
                    self.config['lambda'],
                    cfg['mu'],
                    cfg['n_channels']
                )

            if theory['stable']:
                validation = validate_simulation(multi_stats, theory, self.simulation_settings['epsilon'])
                all_results.append(validation)

                comparison_configs.append({
                    'id': cfg['id'],
                    'description': cfg['description']
                })

                print(f"\nρ = {theory['rho']:.4f}")
                print(f"Макс. ошибка: {validation.max_error*100:.2f}%")
                print(f"r̄ = {multi_stats.avg_queue_length:.4f}")
                print(f"t̄_ож = {multi_stats.avg_wait_time:.4f} мин")

        # Сравнительная статистика
        if all_results:
            print_subsection_header("Сводка по всем конфигурациям")

            print(f"\n{'Конфигурация':<40} | {'Макс ошибка':>10} | {'В допуске':>10}")
            print_separator('-', 65)

            for i, (result, cfg_info) in enumerate(zip(all_results, comparison_configs)):
                status = "✓ ДА" if result.within_tolerance else "✗ НЕТ"
                print(f"{cfg_info['description']:<40} | "
                      f"{result.max_error*100:>8.2f}% | {status:>10}")

            # Рекомендация
            within_tolerance = sum(1 for r in all_results if r.within_tolerance)
            print(f"\nВсего в допуске: {within_tolerance}/{len(all_results)}")

            if within_tolerance == len(all_results):
                print("✓ Все конфигурации адекватны теории")
            else:
                print(f"⚠ {len(all_results) - within_tolerance} конфигурация(й) требует больше реализаций")

    def handle_custom_simulation(self) -> None:
        """Опция 3: Настраиваемое моделирование."""
        print_section_header("Настраиваемое моделирование")

        # Параметры системы
        n_channels = input_integer("\nЧисло каналов обслуживания (n)", default=1, min_val=1)
        if n_channels is None:
            return

        lambda_val = input_float("Интенсивность прибытия λ", default=0.4, min_val=0.01)
        if lambda_val is None:
            return

        mu_val = input_float("Интенсивность обслуживания μ", default=0.5, min_val=0.01)
        if mu_val is None:
            return

        # Выбор распределений
        print("\nВыберите распределение для прибытия:")
        arrival_dist = input_distribution_choice()
        if arrival_dist is None:
            return

        arrival_params = {}
        if arrival_dist != DistributionType.EXPONENTIAL:
            arrival_params = input_distribution_params(arrival_dist) or {}

        print("\nВыберите распределение для обслуживания:")
        service_dist = input_distribution_choice()
        if service_dist is None:
            return

        service_params = {}
        if service_dist != DistributionType.EXPONENTIAL:
            service_params = input_distribution_params(service_dist) or {}

        # Параметры симуляции
        T = input_integer(f"\nДлительность симуляции T (мин)", default=self.simulation_settings['T'])
        if T is None:
            return

        N = input_integer("Число реализаций N", default=self.simulation_settings['N_realizations'])
        if N is None:
            return

        # Запуск
        print("\nЗапуск симуляции...")

        engine = SimulationEngine(
            n_channels=n_channels,
            m_queue=None,
            lambda_param=lambda_val,
            mu_param=mu_val,
            arrival_dist=arrival_dist,
            service_dist=service_dist,
            arrival_params=arrival_params,
            service_params=service_params,
            seed=self.simulation_settings['seed']
        )

        realizations = []
        for i in range(N):
            display_progress(i + 1, N)
            result = engine.run_single_realization(T)
            real_stats = RealizationStatistics.from_simulation_result(result)
            realizations.append(real_stats)

        multi_stats = MultiRealizationStatistics(N_realizations=N, realizations=realizations)
        multi_stats.compute_statistics()

        self.last_results = multi_stats

        # Вывод результатов
        print_subsection_header("Результаты")

        print(f"\nПараметры системы:")
        print(f"  n = {n_channels}, λ = {lambda_val:.4f}, μ = {mu_val:.4f}")
        print(f"  Прибытие: {arrival_dist.name}, Обслуживание: {service_dist.name}")

        print(f"\nХарактеристики:")
        print(f"  λ̄ = {multi_stats.avg_lambda:.6f}")
        print(f"  r̄ = {multi_stats.avg_queue_length:.6f}")
        print(f"  t̄_ож = {multi_stats.avg_wait_time:.6f} мин")
        print(f"  t̄_сист = {multi_stats.avg_system_time:.6f} мин")
        print(f"  A = {multi_stats.avg_absolute_throughput:.6f}")

    def handle_settings(self) -> None:
        """Опция 8: Настройки симуляции."""
        print_section_header("Настройки симуляции")

        print(f"\nТекущие настройки:")
        print(f"  T (длительность): {self.simulation_settings['T']} мин")
        print(f"  N (реализации): {self.simulation_settings['N_realizations']}")
        print(f"  ε (допуск): {self.simulation_settings['epsilon']}")
        print(f"  seed: {self.simulation_settings['seed']}")

        options = {
            1: "Изменить T",
            2: "Изменить N",
            3: "Изменить ε",
            4: "Изменить seed",
            5: "Вернуться в меню"
        }

        choice = input_menu_choice(options, "\nЧто изменить?")

        if choice == 1:
            val = input_integer("Новое значение T (мин)", default=self.simulation_settings['T'])
            if val:
                self.simulation_settings['T'] = val
        elif choice == 2:
            val = input_integer("Новое значение N", default=self.simulation_settings['N_realizations'])
            if val:
                self.simulation_settings['N_realizations'] = val
        elif choice == 3:
            val = input_float("Новое значение ε (0.001-0.1)", default=self.simulation_settings['epsilon'])
            if val and 0.001 <= val <= 0.1:
                self.simulation_settings['epsilon'] = val
        elif choice == 4:
            val = input_integer("Новое значение seed", default=self.simulation_settings['seed'])
            if val:
                self.simulation_settings['seed'] = val

        if choice and choice <= 4:
            print("✓ Настройки обновлены")

    def handle_visualization(self) -> None:
        """Опция 7: Просмотр графиков."""
        print_section_header("Просмотр графиков")

        output_dir = ensure_output_dir()
        png_files = list(output_dir.glob("*.png"))

        if not png_files:
            print("❌ Графиков не найдено. Запустите симуляцию для создания графиков.")
            return

        print(f"\nНайдено {len(png_files)} график(ов):\n")

        for i, f in enumerate(sorted(png_files), 1):
            print(f"  {i}. {f.name}")

        print(f"\nГрафики сохранены в: {output_dir}")

    def run(self) -> None:
        """Главный цикл приложения."""
        if not self.config:
            print("❌ Ошибка при загрузке конфигурации варианта 18")
            sys.exit(1)

        while True:
            choice = self.print_main_menu()

            if choice == 1:
                self.handle_quick_start()
            elif choice == 2:
                self.handle_full_variant18_analysis()
            elif choice == 3:
                self.handle_custom_simulation()
            elif choice == 4:
                print_section_header("Сравнение распределений")
                print("⚠ Опция в разработке")
            elif choice == 5:
                print_section_header("Анализ сходимости")
                print("⚠ Опция в разработке")
            elif choice == 6:
                print_section_header("Валидация")
                self.handle_quick_start()  # Используем быстрый старт как валидацию
            elif choice == 7:
                self.handle_visualization()
            elif choice == 8:
                self.handle_settings()
            elif choice == 9:
                print("\n👋 До свидания!")
                break
            else:
                continue

            try:
                input("\nНажмите Enter для продолжения...")
            except (KeyboardInterrupt, EOFError):
                print("\n⚠ Прерывание пользователем")
                break


def main() -> None:
    """Точка входа в приложение."""
    try:
        app = Lab8Application()
        app.run()
    except KeyboardInterrupt:
        print("\n\n⚠ Программа прервана пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
