from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.bot.filters import IsEligibleFilter
from sesanta.services.country_chooser import CountryChooser
from sesanta.services.user_getter import UserGetter
from sesanta.services.user_set_completeness import UserCompletenessSetter

router = Router()


@router.message(Command("complete"), IsEligibleFilter())
async def handler(
    message: Message,
    db: AsyncIOMotorDatabase,
) -> None:
    user = await UserGetter(db).must_exist(message.chat.id)
    if not CountryChooser.is_allowed(user.selected_countries):
        await message.answer(
            (
                "Упс! В выбранных странах мало клубчан. Может, выбрать хотя бы одну "
                "популярную страну?"
            ),
        )
        return
    await UserCompletenessSetter(db)(message.chat.id, is_complete=True)
    await message.answer(
        "Сохранили твою анкету.\n\n Если захочешь внести изменения, прожми /start",
    )
