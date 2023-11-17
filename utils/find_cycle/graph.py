import dataclasses
import random
from typing import NewType

Vertex = NewType("Vertex", str)


@dataclasses.dataclass(slots=True, frozen=True)
class Edge:
    from_: Vertex
    to: Vertex


class Graph:
    def __init__(self) -> None:
        self.__edges: set[Edge] = set()
        self.__vertexes: set[Vertex] = set()
        self.__random = random.Random()

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
