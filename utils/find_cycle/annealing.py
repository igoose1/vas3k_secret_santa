# ruff: noqa: N802 N803 N806

import dataclasses
import math
import random

from utils.find_cycle.graph import Graph, Vertex


@dataclasses.dataclass(slots=True, frozen=True)
class Result:
    missed: int
    order: list[Vertex]

    def __str__(self) -> str:
        order = ",".join(self.order)
        return f"{self.missed}\t{order}"


class SimulatedAnnealing:
    def __init__(
        self,
        iterations: int,
        graph: Graph,
        randgen: random.Random | None = None,
    ):
        self.iterations = iterations
        self.graph = graph
        self.order = graph.vertexes
        self.random = randgen or random.Random()

    def E(self, order: list[Vertex]) -> int:
        penalty = 0
        for index in range(len(order)):
            if not self.graph.exists(order[index - 1], order[index]):
                # we're okay with `.exists(order[-1], order[0])` as it's a cycle
                penalty += 1
        return penalty

    def F(self, order: list[Vertex]) -> list[Vertex]:
        left = self.random.randrange(len(order))
        right = self.random.randrange(len(order))
        if left > right:
            left, right = right, left
        return order[:left] + order[left : right + 1][::-1] + order[right + 1 :]

    def is_transition(
        self,
        best_E: float,
        candidate_E: float,
        temperature: float,
    ) -> bool:
        if best_E >= candidate_E:
            return True
        probability = math.exp(-(candidate_E - best_E) / temperature)
        return self.random.random() < probability

    def run(self) -> Result:
        temperature = 1.0
        order = self.order
        best_E = self.E(order)
        for index in range(self.iterations):
            candidate = self.F(order)
            candidate_E = self.E(candidate)
            if self.is_transition(best_E, candidate_E, temperature):
                best_E = candidate_E
                order = candidate
            temperature = 1 / (1 + 0.9 * math.log(1 + index))
        return Result(missed=best_E, order=order)
