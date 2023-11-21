import dataclasses
import random
from typing import NewType, Self

from utils.find_cycle.user import FindCycleUser

Vertex = NewType("Vertex", int)


@dataclasses.dataclass(slots=True, frozen=True)
class Edge:
    from_: Vertex
    to: Vertex


class Graph:
    def __init__(self) -> None:
        self.__edges: set[Edge] = set()
        self.__vertexes: set[Vertex] = set()
        self.__random = random.Random()

    @classmethod
    def from_users(cls, users: list[FindCycleUser]) -> Self:
        graph = cls()
        for first_index, first_user in enumerate(users):
            for second_index, second_user in enumerate(users):
                if first_user.slug == second_user.slug:
                    continue
                if first_user.location in second_user.selected:
                    graph.add(Edge(Vertex(second_index), Vertex(first_index)))
        return graph

    def add(self, edge: Edge) -> None:
        self.__edges.add(edge)
        self.__vertexes.add(edge.from_)
        self.__vertexes.add(edge.to)

    def edge_exists(self, edge: Edge) -> bool:
        return edge in self.__edges

    def exists(self, from_: Vertex, to: Vertex) -> bool:
        return self.edge_exists(Edge(from_, to))

    @property
    def vertexes(self) -> list[Vertex]:
        """Returns vertexes in a random order."""
        result = list(self.__vertexes)
        self.__random.shuffle(result)
        return result

    def __len__(self) -> int:
        return len(self.__vertexes)
