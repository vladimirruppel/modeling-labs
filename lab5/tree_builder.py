"""
Построение и визуализация дерева ветвления алгоритма Литтла
"""
from typing import List, Dict, Optional, Tuple
import json


class TreeNode:
    """Узел дерева ветвления"""

    def __init__(self, node_id: int, level: int, lower_bound: int,
                 parent_edge: Optional[Tuple[int, int]] = None,
                 branch_type: str = "root"):
        """
        Инициализация узла

        Args:
            node_id: Идентификатор узла
            level: Уровень в дереве
            lower_bound: Нижняя граница (оценка)
            parent_edge: Ребро, приведшее к этому узлу
            branch_type: Тип ветвления ("root", "include", "exclude")
        """
        self.node_id = node_id
        self.level = level
        self.lower_bound = lower_bound
        self.parent_edge = parent_edge
        self.branch_type = branch_type
        self.children = []
        self.is_pruned = False
        self.is_final = False
        self.path = []

    def add_child(self, child: 'TreeNode'):
        """Добавить дочерний узел"""
        self.children.append(child)

    def __repr__(self):
        return f"Node(id={self.node_id}, level={self.level}, bound={self.lower_bound})"


class BranchingTree:
    """Дерево ветвления алгоритма Литтла"""

    def __init__(self, num_cities: int):
        """
        Инициализация дерева

        Args:
            num_cities: Количество городов
        """
        self.num_cities = num_cities
        self.root = TreeNode(node_id=0, level=0, lower_bound=0, branch_type="root")
        self.all_nodes = [self.root]
        self.node_counter = 1
        self.final_tours = []

    def add_branch(self, parent: TreeNode, lower_bound: int,
                   parent_edge: Tuple[int, int], branch_type: str,
                   path: List[Tuple[int, int]] = None) -> TreeNode:
        """
        Добавить ветвь в дерево

        Args:
            parent: Родительский узел
            lower_bound: Нижняя граница для нового узла
            parent_edge: Ребро, которое привело к этому узлу
            branch_type: Тип ветвления ("include" или "exclude")
            path: Путь к этому узлу

        Returns:
            Новый узел
        """
        new_node = TreeNode(
            node_id=self.node_counter,
            level=parent.level + 1,
            lower_bound=lower_bound,
            parent_edge=parent_edge,
            branch_type=branch_type
        )

        if path:
            new_node.path = path.copy()

        parent.add_child(new_node)
        self.all_nodes.append(new_node)
        self.node_counter += 1

        return new_node

    def mark_pruned(self, node: TreeNode):
        """Отметить узел как отсечённый"""
        node.is_pruned = True

    def mark_final(self, node: TreeNode, tour: List[int]):
        """Отметить узел как финальный с найденным маршрутом"""
        node.is_final = True
        self.final_tours.append((tour, node.lower_bound))

    def get_statistics(self) -> Dict:
        """
        Получить статистику дерева

        Returns:
            Словарь со статистикой
        """
        total_nodes = len(self.all_nodes)
        pruned_nodes = sum(1 for node in self.all_nodes if node.is_pruned)
        final_nodes = sum(1 for node in self.all_nodes if node.is_final)
        max_level = max(node.level for node in self.all_nodes)

        return {
            'total_nodes': total_nodes,
            'pruned_nodes': pruned_nodes,
            'final_nodes': final_nodes,
            'max_level': max_level,
            'final_tours': self.final_tours
        }

    def visualize_text(self) -> str:
        """
        Визуализация дерева в текстовом формате

        Returns:
            Текстовое представление дерева
        """
        lines = []
        lines.append("ДЕРЕВО ВЕТВЛЕНИЯ")
        lines.append("=" * 80)

        def print_node(node: TreeNode, prefix: str = "", is_last: bool = True):
            # Линия подключения
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}Узел {node.node_id} (уровень {node.level})")

            # Информация об узле
            info_prefix = prefix + ("    " if is_last else "│   ")
            lines.append(f"{info_prefix}Оценка: {node.lower_bound}")

            if node.parent_edge:
                lines.append(f"{info_prefix}Ребро: ({node.parent_edge[0]+1}, {node.parent_edge[1]+1})")

            if node.branch_type != "root":
                lines.append(f"{info_prefix}Тип: {node.branch_type}")

            if node.is_pruned:
                lines.append(f"{info_prefix}[ОТСЕЧЕНО]")

            if node.is_final:
                lines.append(f"{info_prefix}[ФИНАЛЬНЫЙ УЗЕЛ]")

            # Рекурсивно выводим детей
            for i, child in enumerate(node.children):
                is_last_child = (i == len(node.children) - 1)
                print_node(child, info_prefix, is_last_child)

        print_node(self.root)

        lines.append("\n" + "=" * 80)
        lines.append("СТАТИСТИКА")
        lines.append("=" * 80)

        stats = self.get_statistics()
        lines.append(f"Всего узлов: {stats['total_nodes']}")
        lines.append(f"Отсечённых узлов: {stats['pruned_nodes']}")
        lines.append(f"Финальных узлов: {stats['final_nodes']}")
        lines.append(f"Максимальный уровень: {stats['max_level']}")

        return "\n".join(lines)

    def visualize_graph(self, filename: str = None) -> str:
        """
        Визуализация дерева в формате Graphviz DOT

        Args:
            filename: Имя файла для сохранения (опционально)

        Returns:
            DOT код для Graphviz
        """
        lines = ['digraph BranchingTree {']
        lines.append('  rankdir=TB;')
        lines.append('  node [shape=box];')

        for node in self.all_nodes:
            # Определяем цвет узла
            if node.is_pruned:
                color = "red"
                label = f"N{node.node_id}\n(отсечено)\n{node.lower_bound}"
            elif node.is_final:
                color = "green"
                label = f"N{node.node_id}\n(финал)\n{node.lower_bound}"
            else:
                color = "lightblue"
                label = f"N{node.node_id}\n{node.lower_bound}"

            lines.append(f'  node_{node.node_id} [label="{label}", fillcolor={color}, style=filled];')

            # Добавляем рёбра к детям
            for child in node.children:
                lines.append(f'  node_{node.node_id} -> node_{child.node_id};')

        lines.append('}')

        dot_code = '\n'.join(lines)

        if filename:
            with open(filename, 'w') as f:
                f.write(dot_code)

        return dot_code

    def export_json(self, filename: str):
        """
        Экспорт дерева в JSON

        Args:
            filename: Имя файла для сохранения
        """
        def node_to_dict(node: TreeNode) -> Dict:
            return {
                'id': node.node_id,
                'level': node.level,
                'lower_bound': node.lower_bound,
                'branch_type': node.branch_type,
                'is_pruned': node.is_pruned,
                'is_final': node.is_final,
                'parent_edge': node.parent_edge,
                'children': [node_to_dict(child) for child in node.children]
            }

        tree_dict = {
            'root': node_to_dict(self.root),
            'statistics': self.get_statistics()
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(tree_dict, f, indent=2, ensure_ascii=False)
