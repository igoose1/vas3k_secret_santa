import datetime

from sesanta.db.schemas.base import AbstractSchema


class MessageSchema(AbstractSchema):
    sender: str
    receiver: str
    text: str
    timestamp: datetime.datetime
