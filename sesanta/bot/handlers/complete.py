from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.bot.filters import IsEligibleFilter
from sesanta.db.schemas.users import UserSchema
from sesanta.services.country_chooser import CountryChooser, hash_country
from sesanta.services.user_getter import UserGetter
from sesanta.services.user_set_completeness import UserCompletenessSetter

router = Router()


class CantContinueError(ValueError):
    """Raised when a user is unable to complete a questionnaire."""


async def is_able_to_continue(
    message: Message,
    user: UserSchema,
) -> None:
    failed = False
    if not CountryChooser.is_allowed(user.selected_countries):
        failed = True
        await message.answer(
            (
                "Упс! В выбранных странах мало клубчан. Может, выбрать хотя бы одну "
                "популярную страну?"
            ),
        )
    if user.location is None:
        failed = True
        await message.answer(
            (
                "Упс! Не понимаю, где сможешь получить подарок. "
                "Проверь, вся ли анкета заполнена."
            ),
        )
    if failed:
        raise CantContinueError


@router.message(Command("complete"), IsEligibleFilter())
async def handler(
    message: Message,
    db: AsyncIOMotorDatabase,
) -> None:
    user = await UserGetter(db).must_exist(message.chat.id)
    try:
        await is_able_to_continue(message, user)
    except CantContinueError:
        return
    await UserCompletenessSetter(db)(message.chat.id, is_completed=True)
    selected = ", ".join(sorted(user.selected_countries, key=hash_country))
    # selected is sorted in a weird order FOR PURPOSE
    await message.answer(
        "Сохранили твою анкету. "
        "Если захочешь внести изменения, прожми /start.\n\n"
        f"Выбранные страны: {selected}.\n\n"
        "Следующим сообщением впиши детали доставки:\n"
        "- Полное имя\n- Адрес\n- Телефон и комментарии по доставке (необязательно)\n"
        "- Твои интересы или пожелания по подарку (необязательно)\n\n",
    )
