from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.bot.handlers.select_countries import generate_select_countries_keyboard
from sesanta.bot.handlers.set_location import generate_set_location_keyboard
from sesanta.services.club_loader import ClubMemberLoader, ClubMemberNotFoundError
from sesanta.services.user_creator import UserUpdater
from sesanta.services.user_eligibility_setter import UserEligibilitySetter
from sesanta.services.user_getter import UserGetter
from sesanta.services.user_is_eligible import IsUserEligible

router = Router(name="start")


@router.message(Command("start"))
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
    passed_criteria = await IsUserEligible(db).check_criteria(message.chat.id)
    if not passed_criteria:
        await message.reply("He подходишь по критериям!")
        return
    user = await UserGetter(db).must_exist(message.chat.id)
    await UserEligibilitySetter(db).users.set_eligibility(
        message.chat.id,
        is_eligible=True,
    )
    await message.answer(
        "Где ты хочешь получить подарок? Можно выбрать только одну страну.",
        reply_markup=generate_set_location_keyboard(offset=0, already_set=user.location),
    )
    await message.answer(
        "Куда ты отправишь подарок? Можно выбрать несколько стран.",
        reply_markup=generate_select_countries_keyboard(
            offset=0,
            already_selected=user.selected_countries,
        ),
    )
