from aiogram import F, Router
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.bot.filters import IsEligibleFilter
from sesanta.bot.handlers.set_location import generate_set_location_keyboard
from sesanta.bot.handlers.understood_select_countries import (
    UNDERSTOOD_TEXT as UNDERSTOOD_SELECT_COUNTRIES,
)
from sesanta.services.user_getter import UserGetter

router = Router()
UNDERSTOOD_TEXT = "Понятно. Надо будет отметить, куда санта отправит мой подарок"


@router.message(F.text == UNDERSTOOD_TEXT, IsEligibleFilter())
async def handler(
    message: Message,
    db: AsyncIOMotorDatabase,
) -> None:
    user = await UserGetter(db).must_exist(message.chat.id)
    await message.answer(
        (
            "Записали\n\n"
            "Где ты хочешь получить подарок?\n\n"
            "<em>Можно выбрать только одну страну.</em>"
        ),
        reply_markup=generate_set_location_keyboard(offset=0, already_set=user.location),
    )
    understood_select_countries_keyboard = ReplyKeyboardBuilder()
    understood_select_countries_keyboard.button(text=UNDERSTOOD_SELECT_COUNTRIES)
    await message.answer(
        (
            "Теперь надо выбрать страны, в которые у тебя получилось бы отправить "
            "подарок. Можно отметить только свою страну, а можно стать международным "
            "сантой. Отправлять посылки заграницу дороже, но зато их приятнее получать."
        ),
        reply_markup=understood_select_countries_keyboard.as_markup(),
    )
