"""
Форматирование и вывод результатов алгоритма Литтла
"""
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import os


class OutputFormatter:
    """Класс для форматирования вывода результатов"""

    def __init__(self, output_dir: str = "output"):
        """
        Инициализация форматтера

        Args:
            output_dir: Директория для сохранения файлов результатов
        """
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def save_solution(self, tour: List[int], cost: int, matrix_size: int,
                     variant: int = None) -> str:
        """
        Сохранить решение в файл

        Args:
            tour: Оптимальный маршрут
            cost: Стоимость маршрута
            matrix_size: Размер матрицы
            variant: Номер варианта (опционально)

        Returns:
            Имя файла с результатом
        """
        filename = f"solution_{self.timestamp}.txt"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("РЕШЕНИЕ ЗАДАЧИ КОММИВОЯЖЕРА\n")
            f.write("=" * 80 + "\n\n")

            if variant:
                f.write(f"Вариант: {variant}\n")

            f.write(f"Размер матрицы: {matrix_size}×{matrix_size}\n")
            f.write(f"Дата и время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("РЕЗУЛЬТАТ\n")
            f.write("-" * 80 + "\n\n")

            tour_str = ' → '.join([str(x+1) for x in tour]) + f" → {tour[0]+1}"
            f.write(f"Оптимальный маршрут: {tour_str}\n")
            f.write(f"Минимальная стоимость: {cost}\n")

        return filename

    def save_detailed_log(self, log_data: str, variant: int = None) -> str:
        """
        Сохранить подробный лог выполнения

        Args:
            log_data: Данные лога
            variant: Номер варианта (опционально)

        Returns:
            Имя файла с логом
        """
        filename = f"algorithm_log_{self.timestamp}.txt"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("ПОДРОБНЫЙ ЛОГ ВЫПОЛНЕНИЯ АЛГОРИТМА ЛИТТЛА\n")
            f.write("=" * 80 + "\n\n")

            if variant:
                f.write(f"Вариант: {variant}\n\n")

            f.write(log_data)

        return filename

    def format_tour_table(self, tour: List[int], costs: List[int]) -> str:
        """
        Форматировать таблицу маршрута

        Args:
            tour: Маршрут (список городов)
            costs: Стоимости переходов

        Returns:
            Отформатированная таблица
        """
        lines = []
        lines.append("\nТАБЛИЦА МАРШРУТА")
        lines.append("─" * 50)
        lines.append("Переход      │ Стоимость")
        lines.append("─" * 50)

        for i in range(len(tour)):
            from_city = tour[i] + 1
            to_city = tour[(i + 1) % len(tour)] + 1
            cost = costs[i]
            lines.append(f"Город {from_city:2d} → Город {to_city:2d} │ {cost:6d}")

        lines.append("─" * 50)
        total_cost = sum(costs)
        lines.append(f"{'ИТОГО':<18}│ {total_cost:6d}")
        lines.append("─" * 50)

        return "\n".join(lines)

    @staticmethod
    def format_comparison_table(python_tour: List[int], python_cost: int,
                               excel_tour: List[int], excel_cost: int) -> str:
        """
        Форматировать таблицу сравнения результатов

        Args:
            python_tour: Маршрут из Python программы
            python_cost: Стоимость из Python программы
            excel_tour: Маршрут из Excel
            excel_cost: Стоимость из Excel

        Returns:
            Отформатированная таблица сравнения
        """
        lines = []
        lines.append("\n" + "=" * 80)
        lines.append("СРАВНЕНИЕ РЕЗУЛЬТАТОВ PYTHON И EXCEL")
        lines.append("=" * 80)

        lines.append("\n┌─────────────────────┬──────────────────────────────────────┐")
        lines.append("│ Метод               │ Результат                            │")
        lines.append("├─────────────────────┼──────────────────────────────────────┤")

        python_tour_str = ' → '.join([str(x+1) for x in python_tour]) + f" → {python_tour[0]+1}"
        lines.append(f"│ Python (Литтла)     │ Маршрут: {python_tour_str[:30]:30s} │")
        lines.append(f"│                     │ Стоимость: {python_cost:<26d} │")

        lines.append("├─────────────────────┼──────────────────────────────────────┤")

        excel_tour_str = ' → '.join([str(x+1) for x in excel_tour]) + f" → {excel_tour[0]+1}"
        lines.append(f"│ Excel (Solver)      │ Маршрут: {excel_tour_str[:30]:30s} │")
        lines.append(f"│                     │ Стоимость: {excel_cost:<26d} │")

        lines.append("└─────────────────────┴──────────────────────────────────────┘")

        if python_cost == excel_cost:
            lines.append("\n✓ Результаты совпадают!")
        else:
            lines.append(f"\n✗ Различие в стоимости: {abs(python_cost - excel_cost)}")

        return "\n".join(lines)

    @staticmethod
    def print_header():
        """Печать заголовка программы"""
        print("\n" + "=" * 80)
        print("ЗАДАЧА О ПЕРЕНАЛАДКЕ ОБОРУДОВАНИЯ")
        print("(Задача коммивояжера)")
        print("=" * 80)
        print("Метод: Алгоритм Литтла (Ветви и границы)")
        print("=" * 80 + "\n")

    @staticmethod
    def print_menu():
        """Печать меню программы"""
        print("\n" + "=" * 80)
        print("МЕНЮ")
        print("=" * 80)
        print("\n1. Решить задачу для варианта 18 (6×6)")
        print("2. Решить задачу для пользовательского файла")
        print("3. Тестовый пример из лекции")
        print("4. Выход\n")

    @staticmethod
    def format_statistics(stats: Dict) -> str:
        """
        Форматировать статистику выполнения

        Args:
            stats: Словарь с статистикой

        Returns:
            Отформатированная статистика
        """
        lines = []
        lines.append("\n" + "=" * 80)
        lines.append("СТАТИСТИКА ВЫПОЛНЕНИЯ АЛГОРИТМА")
        lines.append("=" * 80)

        for key, value in stats.items():
            key_str = key.replace('_', ' ').capitalize()
            if key == 'time_seconds':
                lines.append(f"{key_str}: {value:.4f} сек")
            elif key == 'iterations':
                lines.append(f"{key_str}: {value}")
            else:
                lines.append(f"{key_str}: {value}")

        lines.append("=" * 80 + "\n")

        return "\n".join(lines)

    @staticmethod
    def print_error(message: str):
        """Печать сообщения об ошибке"""
        print(f"\n✗ ОШИБКА: {message}\n")

    @staticmethod
    def print_success(message: str):
        """Печать сообщения об успехе"""
        print(f"\n✓ {message}\n")

    @staticmethod
    def print_info(message: str):
        """Печать информационного сообщения"""
        print(f"\nℹ {message}\n")
