import typing

from sesanta.db.collections.base import AbstractCollection
from sesanta.db.schemas.users import UserSchema
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
        await self.collection.replace_one(
            {"telegram_id": telegram_id},
            UserSchema(
                telegram_id=telegram_id,
                slug=club_member.slug,
                full_name=club_member.full_name,
                upvotes=club_member.upvotes,
                created_at=club_member.created_at,
                membership_expires_at=club_member.membership_expires_at,
            ).dict(),
            upsert=True,
        )
