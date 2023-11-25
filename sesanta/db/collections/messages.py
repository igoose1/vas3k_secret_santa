import datetime
from typing import ClassVar

from sesanta.db.collections.base import AbstractCollection
from sesanta.db.schemas.messages import MessageSchema


class MessageCollection(AbstractCollection):
    name: ClassVar[str] = "messages"

    async def get_chat(self, sender: str, receiver: str) -> list[MessageSchema]:
        filter_ = {
            "$or": [
                {"sender": sender, "receiver": receiver},
                {"sender": receiver, "receiver": sender},
            ],
        }
        cursor = self.collection.find(filter_).sort({"timestamp": 1})
        result: list[MessageSchema] = []
        async for message in cursor:
            result.append(MessageSchema.model_validate(message))
        return result

    async def new(
        self,
        sender: str,
        receiver: str,
        text: str,
        timestamp: datetime.datetime,
    ) -> None:
        await self.collection.insert_one(
            MessageSchema(
                sender=sender,
                receiver=receiver,
                text=text,
                timestamp=timestamp,
            ).model_dump(),
        )
