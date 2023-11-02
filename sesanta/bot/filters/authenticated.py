from aiogram.filters import Filter
from aiogram.types import Message
from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.services.user_getter import UserGetter


class IsAuthenticatedFilter(Filter):
    async def __call__(self, message: Message, db: AsyncIOMotorDatabase) -> bool:
        return (await UserGetter(db)(message.chat.id)) is not None
