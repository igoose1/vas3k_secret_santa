import asyncio

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.services.user_deleter import UserDeleter

router = Router()


@router.message(Command("delete"))
async def handler(
    message: Message,
    db: AsyncIOMotorDatabase,
) -> None:
    await UserDeleter(db)(message.chat.id)
    await message.answer("Аккаунт в клубе удален.")  # I'm sorry
    await asyncio.sleep(5)
    await message.answer("Шутка.")
