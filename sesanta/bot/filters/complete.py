from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message
from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.services.user_getter import UserGetter


class IsCompleteCallbackFilter(Filter):
    def __init__(self, is_completed: bool):
        self.is_completed = is_completed

    async def __call__(
        self,
        callback_query: CallbackQuery,
        db: AsyncIOMotorDatabase,
    ) -> bool:
        user = await UserGetter(db)(callback_query.from_user.id)
        return user is not None and user.is_completed == self.is_completed


class IsCompleteFilter(IsCompleteCallbackFilter):
    async def __call__(
        self,
        message: Message,
        db: AsyncIOMotorDatabase,
    ) -> bool:
        user = await UserGetter(db)(message.chat.id)
        return user is not None and user.is_completed == self.is_completed
