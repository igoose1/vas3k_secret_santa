from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.services.club_loader import ClubMemberLoader, ClubMemberNotFoundError
from sesanta.services.user_creator import UserUpdater

router = Router(name="authenticate")


@router.message(Command("auth"))
async def handler(
    message: Message,
    db: AsyncIOMotorDatabase,
    club_member_loader: ClubMemberLoader,
) -> None:
    telegram_id = message.chat.id
    try:
        member = await club_member_loader(telegram_id)
    except ClubMemberNotFoundError:
        await message.reply("He нашли тебя в клубе. Проверь, привязан ли бот.")
        return
    await message.reply(f"Привет, {member.full_name}!")
    await UserUpdater(db)(telegram_id, member)
