from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.db.collections.users import UserCollection
from sesanta.services.club_loader import ClubMemberLoader, ClubMemberNotFoundError

router = Router(name="authenticate")


@router.message(Command("auth"))
async def handler(
    message: Message,
    db: AsyncIOMotorDatabase,
    club_member_loader: ClubMemberLoader,
) -> None:
    UserCollection(db)
    telegram_id = message.chat.id
    try:
        member = await club_member_loader(telegram_id)
    except ClubMemberNotFoundError:
        await message.reply("увы")
        return
    await message.reply(f"Привет, {member.full_name}!")
