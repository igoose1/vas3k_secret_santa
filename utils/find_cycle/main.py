import sys

import click
import hjson

from utils.basic import User
from utils.find_cycle.annealing import SimulatedAnnealing
from utils.find_cycle.graph import Edge, Graph, Vertex


class FindCycleUser(User):
    selected: set[str]
    location: str


@click.command()
@click.option("--iterations", type=click.INT)
def main(iterations: int) -> None:
    users = [FindCycleUser.model_validate(user) for user in hjson.load(sys.stdin)]
    graph = Graph()
    for first_user in users:
        for second_user in users:
            if first_user.slug == second_user.slug:
                continue
            if first_user.location in second_user.selected:
                graph.add(Edge(Vertex(second_user.slug), Vertex(first_user.slug)))
    annealing = SimulatedAnnealing(iterations, graph)
    result = annealing.run()
    print(result)


if __name__ == "__main__":
    main()
