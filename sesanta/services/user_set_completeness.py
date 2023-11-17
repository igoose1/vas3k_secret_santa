from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.db.collections.users import UserCollection


class UserCompletenessSetter:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.users = UserCollection(db)

    async def __call__(
        self,
        telegram_id: int,
        is_completed: bool,
    ) -> None:
        await self.users.set_completeness(telegram_id, is_completed=is_completed)
