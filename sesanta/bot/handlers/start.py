from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.bot.handlers.understood_set_location import (
    UNDERSTOOD_TEXT as UNDERSTOOD_SET_LOCATION,
)
from sesanta.services.club_loader import ClubMemberLoader, ClubMemberNotFoundError
from sesanta.services.user_creator import UserUpdater
from sesanta.services.user_eligibility_setter import UserEligibilitySetter
from sesanta.services.user_is_eligible import IsUserEligible
from sesanta.settings import settings
from sesanta.utils.plural import RuPlural

router = Router()


@router.message(Command("start"))
async def handler(
    message: Message,
    db: AsyncIOMotorDatabase,
    club_member_loader: ClubMemberLoader,
) -> None:
    await message.answer(
        (
            "Привет! Через меня можно поучаствовать в секретном санте. "
            "Больше подробностей можно найти в посте: \n"
            "➜ [TODO: вставить пост]\n\n"
            "Подожди секунду, надо проверить, что ты из клуба."
        ),
    )
    telegram_id = message.chat.id
    try:
        member = await club_member_loader(telegram_id)
    except ClubMemberNotFoundError:
        await message.answer(
            (
                "He нашли тебя в клубе. Проверь, привязан ли бот.\n\n"
                "https://vas3k.club/user/me/edit/bot/"
            ),
        )
        return
    plural = RuPlural("плюсик", "плюсика", "плюсиков")
    await message.answer(
        (
            f"Нашли тебя в клубе. Ты, должно быть, {member.full_name}.\n\n"
            "В этом году в секретном санте могут участвовать только проверенные люди. "
            "Так, мы уменьшаем риск оставить кого-то без подарка.\n\n"
            "Для твоего участия должно выполняться два пункта из трех:\n"
            f"* У тебя хотя бы {settings.criteria_min_upvotes} "
            f"{plural(settings.criteria_min_upvotes)},\n"
            f"* Твой аккаунт создан не позднее {settings.criteria_max_created_at},\n"
            "* Твоя подписка истекает не раньше "
            f"{settings.criteria_min_membership_expires_at}.\n\n"
            "Подожди еще секунду. Проверим, что у тебя условия выполняются."
        ),
    )
    await UserUpdater(db)(telegram_id, member)
    passed_criteria = await IsUserEligible(db).check_criteria(message.chat.id)
    if not passed_criteria:
        await message.answer(
            (
                "Пока тебе не получится принять участие: чего-то не хватает. Может, "
                'пора <a href="https://vas3k.club/create/">написать хороший пост</a> '
                "или "
                '<a href="https://vas3k.club/user/me/edit/monies/">продлить подписку</a>?'
            ),
        )
        return
    await UserEligibilitySetter(db).users.set_eligibility(
        message.chat.id,
        is_eligible=True,
    )
    understood_set_location_keyboard = ReplyKeyboardBuilder()
    understood_set_location_keyboard.button(text=UNDERSTOOD_SET_LOCATION)
    await message.answer(
        (
            "Тебе можно участвовать!\n\n"
            "Сначала надо выбрать страну, в которой ты готов получить подарок. "
            "Он придет в декабре или в январе. Если будешь переезжать, придумай, "
            "кто примет посылку за тебя.\n\n"
            "Если передумал участвовать, прожми /delete."
        ),
        reply_markup=understood_set_location_keyboard.as_markup(),
    )
