from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.db.collections.users import UserCollection
from sesanta.db.schemas.users import UserSchema


class UserGetter:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.users = UserCollection(db)

    async def __call__(
        self,
        telegram_id: int,
    ) -> UserSchema | None:
        return await self.users.get({"telegram_id": telegram_id})