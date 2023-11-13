from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.bot.filters import IsEligibleFilter
from sesanta.services.country_chooser import CountryChooser, hash_country
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
    selected = ", ".join(sorted(user.selected_countries, key=hash_country))
    # selected is sorted in a weird order FOR PURPOSE
    await message.answer(
        "Сохранили твою анкету. "
        "Если захочешь внести изменения, прожми /start.\n\n"
        f"Выбранные страны: {selected}.\n\n"
        "Следующим сообщением можно вписать детали доставки: "
        "напиши туда адрес и полное имя. "
        "Твой санта укажет эти данные в полях получателя.\n\n"
        "Этот шаг пока можно пропустить. Мы оповестим, когда это будет важно.\n\n",
    )
