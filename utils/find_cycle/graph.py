import collections
import dataclasses
from collections.abc import Sequence
from typing import NewType, Self

from utils.find_cycle.user import FindCycleUser

Vertex = NewType("Vertex", int)


@dataclasses.dataclass(slots=True, frozen=True)
class Edge:
    from_: Vertex
    to: Vertex


class Graph:
    def __init__(self) -> None:
        self.__connected_to: dict[Vertex, set[Vertex]] = collections.defaultdict(set)

    @classmethod
    def from_users(cls, users: list[FindCycleUser]) -> Self:
        graph = cls()
        for first_index, first_user in enumerate(users):
            for second_index, second_user in enumerate(users):
                if first_index == second_index:
                    continue
                if first_user.location in second_user.selected:
                    graph.add(Edge(Vertex(second_index), Vertex(first_index)))
        return graph

    @classmethod
    def to_user(cls, users: list[FindCycleUser], vertex: Vertex) -> FindCycleUser:
        return users[vertex]

    def add(self, edge: Edge) -> None:
        self.__connected_to[edge.from_].add(edge.to)

    def connected_from(self, vertex: Vertex) -> set[Vertex]:
        return self.__connected_to[vertex]

    @property
    def vertexes(self) -> Sequence[Vertex]:
        return list(self.__connected_to.keys())

    def __len__(self) -> int:
        return len(self.__connected_to)
