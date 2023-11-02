from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.db.collections.users import UserCollection
from sesanta.services.club_loader import ClubMember


class UserUpdater:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.users = UserCollection(db)

    async def __call__(
        self,
        telegram_id: int,
        club_member: ClubMember,
    ) -> None:
        await self.users.create_or_update(
            telegram_id,
            club_member=club_member,
        )
