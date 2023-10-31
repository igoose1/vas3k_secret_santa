from sesanta.db.schemas.base import AbstractSchema


class UserSchema(AbstractSchema):
    telegram_id: int
