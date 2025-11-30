import sys
from utils import (
    get_variant_18_problem,
    get_variable_names,
    get_constraint_names,
    print_problem_statement,
    print_solution_analysis,
    verify_solution
)
from simplex_solver_simple import SimpleLinearSolver


def print_menu():
    """Вывести меню"""
    print("\n" + "="*70)
    print("ЛАБОРАТОРНАЯ РАБОТА 3: ТАБЛИЧНЫЙ СИМПЛЕКС-МЕТОД")
    print("="*70)
    print("\nВыберите действие:")
    print("  1. Просмотр постановки задачи")
    print("  2. Решить задачу методом перебора базисов")
    print("  3. Проверить допустимость решения")
    print("  4. Полный анализ решения")
    print("  5. Выход")
    print("-" * 70)


def main():
    print("\n╔════════════════════════════════════════════════════════════════════╗")
    print("║       ЛАБОРАТОРНАЯ РАБОТА 3 - ТАБЛИЧНЫЙ СИМПЛЕКС-МЕТОД            ║")
    print("║            Минимизация затрат на производство мангалов             ║")
    print("║                      Вариант 18 (4 переменные)                      ║")
    print("╚════════════════════════════════════════════════════════════════════╝")

    # Загрузить задачу
    c, A_ub, b_ub, A_eq, b_eq = get_variant_18_problem()

    # Создать решатель
    solver = SimpleLinearSolver(
        c=c,
        A_ub=A_ub,
        b_ub=b_ub,
        variable_names=['x₁', 'x₂', 'x₃', 'x₄'],
        verbose=False
    )

    # Решить задачу один раз
    print("\nРешаю задачу перебором базисов...")
    x_optimal, objective_value, is_feasible = solver.solve()

    if x_optimal is None:
        print("✗ Решение не найдено или задача неограничена")
        return

    print("✓ Оптимальное решение найдено!")

    # Интерактивное меню
    while True:
        print_menu()
        choice = input("Выбор (1-5): ").strip()

        if choice == '1':
            print_problem_statement()

        elif choice == '2':
            print("\n" + "="*70)
            print("ОПТИМАЛЬНОЕ РЕШЕНИЕ")
            print("="*70)
            solver.print_solution(x_optimal, objective_value)

        elif choice == '3':
            verify_solution(x_optimal, c, A_ub, b_ub)

        elif choice == '4':
            # Полный анализ
            print_problem_statement()
            print("\n")
            solver.print_solution(x_optimal, objective_value)
            print("\n")
            print_solution_analysis(x_optimal, objective_value)
            verify_solution(x_optimal, c, A_ub, b_ub)

        elif choice == '5':
            print("\nДо свидания!")
            sys.exit(0)

        else:
            print("✗ Некорректный выбор. Пожалуйста, введите 1-5.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
