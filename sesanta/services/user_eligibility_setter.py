from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.db.collections.users import UserCollection


class UserEligibilitySetter:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.users = UserCollection(db)

    async def __call__(
        self,
        telegram_id: int,
        is_eligible: bool,
    ) -> None:
        await self.users.set_eligibility(telegram_id, is_eligible=is_eligible)
