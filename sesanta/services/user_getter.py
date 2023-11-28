from functools import singledispatchmethod

from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.db.collections.users import UserCollection
from sesanta.db.schemas.users import UserSchema


class UserGetter:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.users = UserCollection(db)

    @singledispatchmethod
    async def __call__(
        self,
        telegram_id: int,
    ) -> UserSchema | None:
        return await self.users.get({"telegram_id": telegram_id})

    @__call__.register
    async def __call__1(
        self,
        slug: str,
    ) -> UserSchema | None:
        return await self.users.get({"slug": slug})

    @singledispatchmethod
    async def must_exist(
        self,
        telegram_id: int,
    ) -> UserSchema:
        if (user := await self(telegram_id)) is not None:
            return user
        msg = f"user with {telegram_id=} doesn't exist"
        raise NotImplementedError(msg)

    @must_exist.register
    async def must_exist_1(
        self,
        slug: str,
    ) -> UserSchema:
        if (user := await self(slug)) is not None:
            return user
        msg = f"user with {slug=} doesn't exist"
        raise NotImplementedError(msg)
