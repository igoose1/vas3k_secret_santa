import datetime
import enum

import pydantic

from sesanta.db.schemas.base import AbstractSchema


class DeliveryStatus(enum.StrEnum):
    NOT_SENT = enum.auto()
    SENT = enum.auto()


class UserSetCompletenessSchema(AbstractSchema):
    is_completed: bool = False


class UserCreateSchema(UserSetCompletenessSchema):
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


class UserFillAddressSchema(AbstractSchema):
    address: str | None = None


class UserSetSantaSchema(AbstractSchema):
    santa: str | None = None


class UserSetDeliveryStatusSchema(AbstractSchema):
    delivery_status: DeliveryStatus = DeliveryStatus.NOT_SENT


class UserSchema(
    UserCreateSchema,
    UserSetEligibilitySchema,
    UserSetLocationSchema,
    UserFillAddressSchema,
    UserSetSantaSchema,
    UserSetDeliveryStatusSchema,
):
    selected_countries: set[str] = pydantic.Field(default_factory=set)
    grandchildren: list[str] = pydantic.Field(default_factory=list)
