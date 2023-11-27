from aiogram import F, Router
from aiogram.types import Message
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.bot.filters import IsEligibleFilter
from sesanta.bot.filters.serving_status import ServingStatusFilter
from sesanta.bot.handlers.select_countries import generate_select_countries_keyboard
from sesanta.services.user_getter import UserGetter
from sesanta.serving_status import ServingStatus

router = Router()
UNDERSTOOD_TEXT = "Понятно. Надо будет отметить, куда я смогу отправить подарок"


@router.message(
    F.text == UNDERSTOOD_TEXT,
    IsEligibleFilter(),
    ServingStatusFilter(ServingStatus.COLLECTING_FORMS),
)
async def handler(
    message: Message,
    db: AsyncIOMotorDatabase,
) -> None:
    user = await UserGetter(db).must_exist(message.chat.id)
    await message.answer(
        (
            "Куда ты отправишь подарок?\n\n"
            "Пожалуйста, просмотри весь список. Не стесняйся отмечать даже непопулярные "
            "страны. Клубчанину из Эквадора или Японии было бы грустно остаться без "
            " подарка, только из-за того, что до таких букв не долистали.\n\n"
            "<em>Можно выбрать несколько стран.</em>"
        ),
        reply_markup=generate_select_countries_keyboard(
            offset=0,
            already_selected=user.selected_countries,
        ),
    )
    await message.answer(
        "Для завершения анкеты прожми /complete",
        reply_markup=ReplyKeyboardRemove(),
    )
