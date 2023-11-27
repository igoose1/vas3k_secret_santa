import sys

import click
import hjson

from utils.find_cycle.graph import Graph
from utils.find_cycle.search import OrderSearcher
from utils.find_cycle.user import FindCycleUser


@click.command()
def main() -> None:
    users = [FindCycleUser.model_validate(user) for user in hjson.load(sys.stdin)]
    graph = Graph.from_users(users)
    result = OrderSearcher(graph).run()
    order = [Graph.to_user(users, vertex).slug for vertex in result.order]
    print(result.missed, ",".join(order))


if __name__ == "__main__":
    main()
