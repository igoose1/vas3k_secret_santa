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
@click.option("--not-completed-only", default=False, help="Only completed")
@click.option("--no-address-only", default=False, help="Only without address")
async def main(
    completed_only: bool,
    not_completed_only: bool,
    no_address_only: bool,
) -> None:
    """Export users to stdout."""
    db = AsyncIOMotorClient(str(settings.mongo_uri))[settings.mongo_db]
    collection = UserCollection(db)

    result: list[User] = []
    filter_ = {"is_completed": True} if completed_only else {}
    filter_ = {}
    if completed_only:
        filter_.update({"is_completed": True})
    if not_completed_only:
        filter_.update({"is_completed": False})
    if no_address_only:
        filter_.update({"address": None})
    async for user in collection.get_all(filter_):
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
