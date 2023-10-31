from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router(name="start")


@router.message(CommandStart())
async def handler(message: Message) -> None:
    await message.answer(f"Hi, {message.chat.full_name}!")
