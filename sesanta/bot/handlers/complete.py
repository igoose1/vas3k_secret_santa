from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.bot.filters import IsEligibleFilter
from sesanta.services.country_chooser import CountryChooser
from sesanta.services.user_getter import UserGetter
from sesanta.services.user_set_completeness import UserCompletenessSetter

router = Router(name="complete")


@router.message(Command("complete"), IsEligibleFilter())
async def handler(
    message: Message,
    db: AsyncIOMotorDatabase,
) -> None:
    user = await UserGetter(db).must_exist(message.chat.id)
    if not CountryChooser.is_allowed(user.selected_countries):
        await message.reply(
            "Упс! В выбранных странах недостаточно клубчан. "
            "Выбери более популярные страны.",
        )
        return
    await UserCompletenessSetter(db)(message.chat.id, is_complete=True)
    await message.reply("Ура! Сохранили твою анкету.")
