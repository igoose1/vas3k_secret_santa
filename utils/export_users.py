import json as jsonlib
import sys

import asyncclick as click
import hjson
from motor.motor_asyncio import AsyncIOMotorClient
from typing_extensions import TypedDict

from sesanta.db.collections.users import UserCollection
from sesanta.settings import settings


class User(TypedDict):
    slug: str
    location: str | None
    selected: list[str]
    is_completed: bool


@click.command()
@click.option("--completed-only", default=False, help="Only completed")
@click.option("--json", default=False, help="Print in JSON format")
async def main(completed_only: bool, json: bool) -> None:
    """Export users to stdout."""
    db = AsyncIOMotorClient(str(settings.mongo_uri))[settings.mongo_db]
    collection = UserCollection(db)

    result: list[User] = []
    filter_ = {"is_completed": True} if completed_only else {}
    async for user in collection.get_all(filter_):
        result.append(
            User(
                slug=user.slug,
                location=user.location,
                selected=list(user.selected_countries),
                is_completed=user.is_completed,
            ),
        )

    if json:
        jsonlib.dump(result, sys.stdout, ensure_ascii=False)
    else:
        hjson.dump(result, sys.stdout)


if __name__ == "__main__":
    main(_anyio_backend="asyncio")
