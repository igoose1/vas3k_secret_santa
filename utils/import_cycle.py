import sys

import asyncclick as click
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import TypeAdapter

from sesanta.db.collections.users import UserCollection
from sesanta.settings import settings
from utils.basic import User

UserListAdapter = TypeAdapter(list[User])


@click.command()
async def main() -> None:
    """Set Santas and grandchildren from `utils/find_cycle`."""
    db = AsyncIOMotorClient(str(settings.mongo_uri))[settings.mongo_db]
    collection = UserCollection(db)

    slugs = sys.stdin.read().strip().split(",")

    await collection.clear_santa_information()
    for index, user in enumerate(slugs):
        santa, grandchild = slugs[index - 1], slugs[(index + 1) % len(slugs)]
        await collection.set_santa_information(
            user,
            santa,
            grandchild,
        )


if __name__ == "__main__":
    main(_anyio_backend="asyncio")
