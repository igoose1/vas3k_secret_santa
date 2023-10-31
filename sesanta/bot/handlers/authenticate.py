from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="start")


@router.message(Command("auth"))
async def handler(message: Message) -> None:
    await message.answer(f"Hi, {message.chat.full_name}!")
