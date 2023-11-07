from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.bot.filters import IsAuthenticatedFilter
from sesanta.bot.handlers.select_countries import generate_select_countries_keyboard
from sesanta.bot.handlers.set_location import generate_set_location_keyboard
from sesanta.services.user_eligibility_setter import UserEligibilitySetter
from sesanta.services.user_getter import UserGetter
from sesanta.services.user_is_eligible import IsUserEligible

router = Router(name="authenticate")


@router.message(Command("auth"), IsAuthenticatedFilter())
async def handler(
    message: Message,
    db: AsyncIOMotorDatabase,
) -> None:
    passed_criteria = await IsUserEligible(db).check_criteria(message.chat.id)
    if not passed_criteria:
        await message.reply("He подходишь!")
        return
    await message.reply("Подходишь по критериям!")
    user = await UserGetter(db)(message.chat.id)
    if user is None:
        msg = "never happens"
        raise NotImplementedError(msg)
    await UserEligibilitySetter(db).users.set_eligibility(
        message.chat.id,
        is_eligible=True,
    )
    await message.answer(
        "Где ты хочешь получить подарок? Можно выбрать только одну страну.",
        reply_markup=generate_set_location_keyboard(offset=0),
    )
    await message.answer(
        "Куда ты отправишь подарок? Можно выбрать несколько стран.",
        reply_markup=generate_select_countries_keyboard(
            offset=0,
            already_selected=user.selected_countries,
        ),
    )
