import datetime

import pydantic

from sesanta.db.schemas.base import AbstractSchema


class UserCreateSchema(AbstractSchema):
    telegram_id: int
    slug: str
    full_name: str
    upvotes: int
    created_at: datetime.datetime
    membership_expires_at: datetime.datetime


class UserSetEligibilitySchema(AbstractSchema):
    is_eligible: bool = False


class UserSetLocationSchema(AbstractSchema):
    location: str | None = None


class UserSchema(UserCreateSchema, UserSetEligibilitySchema):
    selected_countries: set[str] = pydantic.Field(default_factory=set)
