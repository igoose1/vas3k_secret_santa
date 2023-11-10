from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.db.collections.users import UserCollection


class UserDeleter:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.users = UserCollection(db)

    async def __call__(
        self,
        telegram_id: int,
    ) -> None:
        await self.users.delete(telegram_id)
