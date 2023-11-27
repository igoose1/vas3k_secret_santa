import random
import sys
from collections import defaultdict

import click
import graphviz
import hjson
from pydantic import TypeAdapter

from utils.basic import User

UserListAdapter = TypeAdapter(list[User])


def random_color() -> str:
    def rand() -> int:
        return random.randint(100, 255)

    return f"#{rand():02X}{rand():02X}{rand():02X}"


def group_by_countries(
    users: list[User],
    combine_if_less: int | None = None,
) -> dict[str, list[str]]:
    groups = defaultdict(list)
    for user in users:
        groups[user.location].append(user.slug)
    if combine_if_less is None:
        return groups
    popular_groups = {"Other": []}
    for country, users in groups.items():
        if len(users) <= combine_if_less:
            popular_groups["Other"] += users
        else:
            popular_groups[country] = users
    return popular_groups


@click.command()
def main() -> None:
    """Print graphviz (DOT) code to draw a graph."""
    users = UserListAdapter.validate_python(hjson.load(sys.stdin))
    graph = graphviz.Digraph("Santas to grandchildren")
    groups = group_by_countries(users, combine_if_less=5)
    for country, country_users in groups.items():
        with graph.subgraph(name=f"cluster_{country}") as subgraph:  # type: ignore
            subgraph.attr(style="filled", color=random_color())
            for slug in country_users:
                subgraph.node(slug)
    for user in users:
        for grandchild in user.grandchildren:
            graph.edge(user.slug, grandchild)
    sys.stdout.write(graph.source)


if __name__ == "__main__":
    main()
