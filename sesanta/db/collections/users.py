import typing

from sesanta.db.collections.base import AbstractCollection
from sesanta.db.schemas.users import UserSchema


class UserCollection(AbstractCollection):
    name: typing.ClassVar[str] = "users"

    async def get(self, filter_: dict[str, typing.Any]) -> UserSchema | None:
        if (document := await self.collection.find_one(filter_)) is not None:
            return UserSchema.model_validate(document)
        return None
