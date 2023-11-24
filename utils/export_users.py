import sys

import asyncclick as click
import hjson
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import TypeAdapter

from sesanta.db.collections.users import UserCollection
from sesanta.settings import settings
from utils.basic import User

UserListAdapter = TypeAdapter(list[User])


@click.command()
@click.option("--completed-only", default=False, help="Only completed")
async def main(completed_only: bool) -> None:
    """Export users to stdout."""
    db = AsyncIOMotorClient(str(settings.mongo_uri))[settings.mongo_db]
    collection = UserCollection(db)

    result: list[User] = []
    filter_ = {"is_completed": True} if completed_only else {}
    async for user in collection.get_all(filter_):
        result.append(
            User(
                slug=user.slug,
                telegram_id=user.telegram_id,
                location=user.location,
                selected=list(user.selected_countries),
                is_completed=user.is_completed,
            ),
        )

    adapted_result = UserListAdapter.dump_python(result)
    hjson.dump(adapted_result, sys.stdout)


if __name__ == "__main__":
    main(_anyio_backend="asyncio")
