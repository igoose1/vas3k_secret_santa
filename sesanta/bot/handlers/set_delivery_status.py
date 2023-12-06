from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.bot.filters import IsCompleteCallbackFilter, IsCompleteFilter
from sesanta.bot.filters.serving_status import ServingStatusFilter
from sesanta.db.collections.users import UserCollection
from sesanta.db.schemas.users import DeliveryStatus
from sesanta.serving_status import ServingStatus

router = Router()

CONFIRM_BUTTON_TEXT = "Да, мой подарок в пути"


class ConfirmSetDeliveryStatusCallback(CallbackData, prefix="condelivery"):
    ...


@router.message(
    Command("i_sent"),
    IsCompleteFilter(is_completed=True),
    ServingStatusFilter(ServingStatus.SENDING_GIFTS),
)
async def handler(
    message: Message,
) -> None:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=CONFIRM_BUTTON_TEXT,
        callback_data=ConfirmSetDeliveryStatusCallback(),
    )
    await message.answer(
        "Отметить подарок отправленным?",
        reply_markup=keyboard.as_markup(),
    )


@router.callback_query(
    ConfirmSetDeliveryStatusCallback.filter(),
    IsCompleteCallbackFilter(is_completed=True),
    ServingStatusFilter(ServingStatus.SENDING_GIFTS),
)
async def callback_handler(
    callback_query: CallbackQuery,
    callback_data: ConfirmSetDeliveryStatusCallback,
    db: AsyncIOMotorDatabase,
) -> None:
    await UserCollection(db).set_delivery_status(
        callback_query.from_user.id,
        DeliveryStatus.SENT,
    )
    if callback_query.message is None:
        await callback_query.answer("Отметили, что твой подарок едет!")
        return
    await callback_query.message.answer(
        "Отметили, что твой подарок едет! Мы никак не оповестили подопечного. "
        "Если это важно, поделись трек-номером или примерными датами доставки через чаты "
        "— /get_chats.",
    )
