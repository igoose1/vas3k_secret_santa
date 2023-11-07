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
from sesanta.settings import settings

router = Router(name="start")


@router.message(Command("start"))
async def handler(
    message: Message,
    db: AsyncIOMotorDatabase,
    club_member_loader: ClubMemberLoader,
) -> None:
    await message.reply(
        (
            "Привет! Через меня можно поучаствовать в секретном санте. "
            "Подожди секунду, надо проверить, что ты из клуба."
        ),
    )
    telegram_id = message.chat.id
    try:
        member = await club_member_loader(telegram_id)
    except ClubMemberNotFoundError:
        await message.reply(
            (
                "He нашли тебя в клубе. Проверь, привязан ли бот.\n\n"
                "https://vas3k.club/user/me/edit/bot/"
            ),
        )
        return
    await message.reply(
        (
            f"Нашли тебя в клубе. Ты, должно быть, {member.full_name}.\n\n"
            "В этом году в секретном санте могут участвовать только проверенные люди. "
            "Так мы уменьшаем риск оставить кого-то без подарка.\n\n"
            "Для твоего участия должно выполняться два пункта из трех:\n"
            f"* У тебя хотя бы столько плюсиков: {settings.criteria_min_upvotes},\n"
            f"* Твой аккаунт создан не позднее {settings.criteria_max_created_at},\n"
            "* Твоя подписка истекает не раньше "
            f"{settings.criteria_min_membership_expires_at}.\n\n"
            "Подожди еще секунду. Проверим, что у тебя условия выполняются."
        ),
    )
    await UserUpdater(db)(telegram_id, member)
    passed_criteria = await IsUserEligible(db).check_criteria(message.chat.id)
    if not passed_criteria:
        await message.reply("He подходишь по критериям.")
        return
    user = await UserGetter(db).must_exist(message.chat.id)
    await UserEligibilitySetter(db).users.set_eligibility(
        message.chat.id,
        is_eligible=True,
    )
    await message.answer(
        (
            "Отлично!\n\n"
            "Где ты хочешь получить подарок?\n\n"
            "<em>Можно выбрать только одну страну.</em>"
        ),
        reply_markup=generate_set_location_keyboard(offset=0, already_set=user.location),
    )
    await message.answer(
        "Куда ты отправишь подарок?\n\n<em>Можно выбрать несколько стран.</em>",
        reply_markup=generate_select_countries_keyboard(
            offset=0,
            already_selected=user.selected_countries,
        ),
    )
    await message.answer(
        "Для завершения анкеты прожми /complete",
    )
