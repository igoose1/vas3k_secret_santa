import dataclasses

from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.db.collections.users import UserCollection
from sesanta.db.schemas.users import UserCreateSchema
from sesanta.settings import settings

NUMBER_OF_CRITERIA_TO_PASS = 2


@dataclasses.dataclass(slots=True)
class PassedCriteria:
    by_upvotes: bool
    by_created_at: bool
    by_membership_expires_at: bool

    def __bool__(self) -> bool:
        return self.number >= NUMBER_OF_CRITERIA_TO_PASS

    @property
    def number(self) -> int:
        return [
            self.by_upvotes,
            self.by_created_at,
            self.by_membership_expires_at,
        ].count(True)


class IsUserEligible:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.users = UserCollection(db)

    async def __call__(
        self,
        telegram_id: int,
    ) -> bool:
        return bool(await self.check_criteria(telegram_id))

    async def check_criteria(self, telegram_id: int) -> PassedCriteria:
        user: UserCreateSchema = UserCreateSchema.model_validate(
            await self.users.get({"telegram_id": telegram_id}),
        )
        return PassedCriteria(
            by_upvotes=user.upvotes >= settings.criteria_min_upvotes,
            by_created_at=user.created_at.date() <= settings.criteria_max_created_at,
            by_membership_expires_at=user.membership_expires_at.date()
            >= settings.criteria_min_membership_expires_at,
        )
