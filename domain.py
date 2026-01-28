from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class ProcessNode:
    """
    Узел бизнес-процесса.
    """

    id: str
    title: str
    description: str = ""
    node_type: str = "task"  # task | start | end | gateway_and | gateway_or | gateway_xor | subprocess
    color: str = "#00ff00"
    lane: Optional[str] = None  # строка (отдел/подпроцесс)


@dataclass
class ProcessEdge:
    """
    Связь (переход) между узлами процесса.
    """

    from_id: str
    to_id: str
    label: str = ""
    branch_type: str = "default"  # default | yes | no | and | or


@dataclass
class ProcessGraph:
    """
    Модель бизнес-процесса как графа.
    """

    nodes: Dict[str, ProcessNode] = field(default_factory=dict)
    edges: List[ProcessEdge] = field(default_factory=list)

    def add_node(self, node: ProcessNode) -> None:
        """
        Добавляет узел в граф.
        """
        self.nodes[node.id] = node

    def add_edge(self, edge: ProcessEdge) -> None:
        """
        Добавляет связь в граф.
        """
        self.edges.append(edge)

    def to_dict(self) -> Dict:
        """
        Преобразует граф в словарь для сериализации.
        """
        lanes = sorted({node.lane for node in self.nodes.values() if node.lane})
        return {
            "nodes": [
                {
                    "id": node.id,
                    "title": node.title,
                    "description": node.description,
                    "node_type": node.node_type,
                    "color": node.color,
                    "lane": node.lane,
                }
                for node in self.nodes.values()
            ],
            "edges": [
                {
                    "from": edge.from_id,
                    "to": edge.to_id,
                    "label": edge.label,
                    "branch_type": edge.branch_type,
                }
                for edge in self.edges
            ],
            "lanes": lanes,
        }

    @classmethod
    def from_text_lines(cls, lines: List[str]) -> "ProcessGraph":
        """
        Создает простой линейный процесс из списка строк.

        Каждая строка становится узлом, а между соседними узлами
        создаются связи по порядку.
        """
        graph = cls()
        prev_node_id: Optional[str] = None

        for index, raw_line in enumerate(lines):
            title = raw_line.strip()
            if not title:
                continue

            node_id = f"step_{index + 1}"
            node = ProcessNode(id=node_id, title=title)
            graph.add_node(node)

            if prev_node_id is not None:
                edge = ProcessEdge(from_id=prev_node_id, to_id=node_id)
                graph.add_edge(edge)

            prev_node_id = node_id

        return graph

    @classmethod
    def from_structured_steps(cls, steps: List[Dict[str, str]]) -> "ProcessGraph":
        """
        Создает процесс из структурированного списка шагов.

        Каждый шаг задается словарем вида:
        {"title": "Описание", "department": "Отдел_1", "type": "task"}
        """
        graph = cls()

        # Сначала создаём узлы в порядке следования шагов
        ordered_nodes: List[ProcessNode] = []

        for index, step in enumerate(steps):
            title = (step.get("title") or "").strip()
            department = (step.get("department") or "").strip() or None
            node_type = (step.get("type") or "task").strip() or "task"

            if not title:
                continue

            node_id = f"step_{index + 1}"
            node = ProcessNode(id=node_id, title=title, lane=department, node_type=node_type)
            graph.add_node(node)
            ordered_nodes.append(node)

        # Затем создаём связи с учётом условий
        for index, node in enumerate(ordered_nodes):
            # Связь от предыдущего шага к текущему
            if index > 0:
                prev_node = ordered_nodes[index - 1]
                # Если текущий узел является условием, всегда соединяем предыдущий с ним
                if node.node_type.startswith("cond_"):
                    graph.add_edge(ProcessEdge(from_id=prev_node.id, to_id=node.id))
                # Если предыдущий узел не условие, соединяем его с текущим как обычный переход
                elif not prev_node.node_type.startswith("cond_"):
                    graph.add_edge(ProcessEdge(from_id=prev_node.id, to_id=node.id))

            # Ветвление для условий
            if node.node_type == "cond_yes_no":
                # Да → следующий шаг
                if index + 1 < len(ordered_nodes):
                    graph.add_edge(
                        ProcessEdge(
                            from_id=node.id,
                            to_id=ordered_nodes[index + 1].id,
                            branch_type="yes",
                        )
                    )
                # Нет → шаг через один
                if index + 2 < len(ordered_nodes):
                    graph.add_edge(
                        ProcessEdge(
                            from_id=node.id,
                            to_id=ordered_nodes[index + 2].id,
                            branch_type="no",
                        )
                    )

            elif node.node_type == "cond_and":
                # И → следующий и шаг через один
                if index + 1 < len(ordered_nodes):
                    graph.add_edge(
                        ProcessEdge(
                            from_id=node.id,
                            to_id=ordered_nodes[index + 1].id,
                            branch_type="and",
                        )
                    )
                if index + 2 < len(ordered_nodes):
                    graph.add_edge(
                        ProcessEdge(
                            from_id=node.id,
                            to_id=ordered_nodes[index + 2].id,
                            branch_type="and",
                        )
                    )

            elif node.node_type == "cond_or":
                # ИЛИ → следующий и шаг через один
                if index + 1 < len(ordered_nodes):
                    graph.add_edge(
                        ProcessEdge(
                            from_id=node.id,
                            to_id=ordered_nodes[index + 1].id,
                            branch_type="or",
                        )
                    )
                if index + 2 < len(ordered_nodes):
                    graph.add_edge(
                        ProcessEdge(
                            from_id=node.id,
                            to_id=ordered_nodes[index + 2].id,
                            branch_type="or",
                        )
                    )

        return graph
