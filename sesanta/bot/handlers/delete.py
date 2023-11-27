import asyncio

from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.bot.filters.serving_status import ServingStatusFilter
from sesanta.services.user_deleter import UserDeleter
from sesanta.serving_status import ServingStatus

router = Router()

CONFIRM_BUTTON_TEXT = "Да, точно удалить"


class ConfirmDeletionCallback(CallbackData, prefix="condel"):
    ...


@router.message(Command("delete"), ServingStatusFilter(ServingStatus.COLLECTING_FORMS))
async def handler(
    message: Message,
) -> None:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=CONFIRM_BUTTON_TEXT,
        callback_data=ConfirmDeletionCallback(),
    )
    await message.answer(
        "Удалить аккаунт? Все данные сотрутся и их нельзя будет вернуть.",
        reply_markup=keyboard.as_markup(),
    )


@router.callback_query(
    ConfirmDeletionCallback.filter(),
    ServingStatusFilter(ServingStatus.COLLECTING_FORMS),
)
async def confirm_handler(
    callback_query: CallbackQuery,
    callback_data: ConfirmDeletionCallback,
    db: AsyncIOMotorDatabase,
) -> None:
    await UserDeleter(db)(callback_query.from_user.id)
    if callback_query.message is None:
        await callback_query.answer("Удалено", show_alert=True)
    else:
        await callback_query.message.answer("Аккаунт в клубе удален.")  # I'm sorry
        await asyncio.sleep(5)
        await callback_query.message.answer("Шутка")
        await callback_query.answer()
