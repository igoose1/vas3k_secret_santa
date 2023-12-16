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
async def main() -> None:
    """Export users to stdout."""
    db = AsyncIOMotorClient(str(settings.mongo_uri))[settings.mongo_db]
    collection = UserCollection(db)

    result: list[User] = []
    async for user in collection.get_all({}):
        result.append(
            User(
                slug=user.slug,
                telegram_id=user.telegram_id,
                address=user.address,
                location=user.location,
                selected=list(user.selected_countries),
                is_completed=user.is_completed,
                santa=user.santa,
                grandchildren=user.grandchildren,
                delivery_status=user.delivery_status,
            ),
        )

    adapted_result = UserListAdapter.dump_python(result)
    hjson.dump(adapted_result, sys.stdout)


if __name__ == "__main__":
    main(_anyio_backend="asyncio")
