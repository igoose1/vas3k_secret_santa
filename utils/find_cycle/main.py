import random
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
@click.option("--iterations", type=int)
@click.option("--attempts", default=1)
def main(iterations: int, attempts: int) -> None:
    users = [FindCycleUser.model_validate(user) for user in hjson.load(sys.stdin)]
    graph = Graph()
    for first_index, first_user in enumerate(users):
        for second_index, second_user in enumerate(users):
            if first_user.slug == second_user.slug:
                continue
            if first_user.location in second_user.selected:
                graph.add(Edge(Vertex(second_index), Vertex(first_index)))
    randgen = random.Random()
    best = None
    local = None
    for attempt in range(attempts):
        annealing = SimulatedAnnealing(
            iterations,
            graph,
            order=local.order if local else None,
            randgen=randgen,
        )
        local = annealing.run()
        if best is None or local.missed < best.missed:
            best = local
    if best is None:
        msg = "haven't attempted to run"
        raise ValueError(msg)
    order = [users[index].slug for index in best.order]
    print(best.missed, ",".join(order))


if __name__ == "__main__":
    main()
