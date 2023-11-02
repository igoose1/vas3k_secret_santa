from aiogram.filters import Filter
from aiogram.types import Message
from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.services.user_getter import UserGetter


class IsEligibleFilter(Filter):
    async def __call__(self, message: Message, db: AsyncIOMotorDatabase) -> bool:
        user = await UserGetter(db)(message.chat.id)
        return user is not None and user.is_eligible
