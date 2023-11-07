import typing

from sesanta.db.collections.base import AbstractCollection
from sesanta.db.schemas.users import (
    UserCreateSchema,
    UserSchema,
    UserSetEligibilitySchema,
    UserSetLocationSchema,
)
from sesanta.services.club_loader import ClubMember


class UserCollection(AbstractCollection):
    name: typing.ClassVar[str] = "users"

    async def get(self, filter_: dict[str, typing.Any]) -> UserSchema | None:
        if (document := await self.collection.find_one(filter_)) is not None:
            return UserSchema.model_validate(document)
        return None

    async def create_or_update(
        self,
        telegram_id: int,
        *,
        club_member: ClubMember,
    ) -> None:
        await self.collection.update_one(
            {"telegram_id": telegram_id},
            {
                "$set": UserCreateSchema(
                    telegram_id=telegram_id,
                    slug=club_member.slug,
                    full_name=club_member.full_name,
                    upvotes=club_member.upvotes,
                    created_at=club_member.created_at,
                    membership_expires_at=club_member.membership_expires_at,
                ).dict(),
            },
            upsert=True,
        )

    async def set_eligibility(
        self,
        telegram_id: int,
        *,
        is_eligible: bool,
    ) -> None:
        await self.collection.update_one(
            {"telegram_id": telegram_id},
            {"$set": UserSetEligibilitySchema(is_eligible=is_eligible).dict()},
        )

    async def set_location(
        self,
        telegram_id: int,
        *,
        location: str,
    ) -> None:
        await self.collection.update_one(
            {"telegram_id": telegram_id},
            {"$set": UserSetLocationSchema(location=location).dict()},
        )

    async def select_country(
        self,
        telegram_id: int,
        *,
        country: str,
    ) -> None:
        await self.collection.update_one(
            {"telegram_id": telegram_id},
            {"$addToSet": {"selected_countries": country}},
        )

    async def unselect_country(
        self,
        telegram_id: int,
        *,
        country: str,
    ) -> None:
        await self.collection.update_one(
            {"telegram_id": telegram_id},
            {"$pull": {"selected_countries": country}},
        )
