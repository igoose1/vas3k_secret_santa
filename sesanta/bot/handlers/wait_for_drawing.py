from aiogram import Router
from aiogram.types import Message

from sesanta.bot.filters.serving_status import ServingStatusFilter
from sesanta.settings import ServingStatus

router = Router()


@router.message(ServingStatusFilter(ServingStatus.DRAWING_LOTS))
async def handler(
    message: Message,
) -> None:
    await message.answer(
        "Проводится жеребьевка. Сейчас бот неактивный. Подожди еще чуть-чуть.",
    )
