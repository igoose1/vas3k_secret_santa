import dataclasses
import random

from utils.find_cycle.graph import Graph, Vertex


@dataclasses.dataclass(slots=True, frozen=True)
class Result:
    graph: Graph
    order: list[Vertex]

    @property
    def missed(self) -> int:
        if not self.order:
            return 0
        result = 0
        current = self.order[-1]
        for next_ in self.order:
            if next_ not in self.graph.connected_from(current):
                result += 1
            current = next_
        return result


class OrderSearcher:
    def __init__(self, graph: Graph):
        self.graph = graph

    def walk(self, current: Vertex, visited: set[Vertex]) -> list[Vertex]:
        visited.add(current)
        go_to: Vertex | None = None
        go_to_factor = -1
        for next_ in self.graph.connected_from(current):
            if next_ in visited:
                continue
            factor = len(self.graph.connected_from(next_))
            if go_to is None or go_to_factor > factor:
                go_to = next_
                go_to_factor = factor
        if go_to is None:
            return [current]
        return [current, *self.walk(go_to, visited)]

    def run(self) -> Result:
        result = Result(self.graph, [])
        while len(result.order) != len(self.graph) or result.missed:
            order = self.walk(
                random.choice(self.graph.vertexes),
                set(),
            )
            result = Result(
                self.graph,
                order,
            )
        return result
