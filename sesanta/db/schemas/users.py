import datetime

from sesanta.db.schemas.base import AbstractSchema


class UserSchema(AbstractSchema):
    telegram_id: int
    slug: str
    full_name: str
    upvotes: int
    created_at: datetime.datetime
    membership_expires_at: datetime.datetime
