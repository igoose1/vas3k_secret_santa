import typing

from aiogram import Router
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.bot.filters import IsEligibleFilter
from sesanta.db.collections.users import UserCollection
from sesanta.services.country_chooser import COUNTRIES, HASH_TO_COUNTRY, hash_country

router = Router(name="set_location")


class SetLocationCallback(CallbackData, prefix="sl"):
    country_hash: str

    @classmethod
    def from_country(cls, country: str) -> typing.Self:
        return cls(country_hash=hash_country(country))

    @property
    def country(self) -> str | None:
        return HASH_TO_COUNTRY.get(self.country_hash)


class SetLocationPagerCallback(CallbackData, prefix="slp"):
    offset: int


COUNTRIES_IN_ONE_KEYBOARD = 16


def generate_set_location_keyboard(offset: int) -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()
    for country in COUNTRIES[offset : offset + COUNTRIES_IN_ONE_KEYBOARD]:
        keyboard_builder.button(
            text=country,
            callback_data=SetLocationCallback.from_country(country),
        )
    if offset:
        keyboard_builder.button(
            text="⬅️",
            callback_data=SetLocationPagerCallback(
                offset=offset - COUNTRIES_IN_ONE_KEYBOARD,
            ),
        )
    if offset + COUNTRIES_IN_ONE_KEYBOARD < len(COUNTRIES):
        keyboard_builder.button(
            text="➡️",
            callback_data=SetLocationPagerCallback(
                offset=offset + COUNTRIES_IN_ONE_KEYBOARD,
            ),
        )
    keyboard_builder.adjust(2)
    return keyboard_builder.as_markup()


@router.callback_query(SetLocationPagerCallback.filter())
async def pager_handler(
    callback_query: CallbackQuery,
    callback_data: SetLocationPagerCallback,
) -> None:
    if callback_query.message is None:
        await callback_query.answer("Сообщение устарело")
        return
    await callback_query.message.edit_reply_markup(
        reply_markup=generate_set_location_keyboard(callback_data.offset),
    )


@router.message(IsEligibleFilter())
async def handler(
    message: Message,
    db: AsyncIOMotorDatabase,
) -> None:
    await message.answer(
        "Где ты?",
        reply_markup=generate_set_location_keyboard(offset=0),
    )


@router.callback_query(SetLocationCallback.filter())
async def callback_handler(
    callback_query: CallbackQuery,
    callback_data: SetLocationCallback,
    db: AsyncIOMotorDatabase,
) -> None:
    country = callback_data.country
    if callback_query.message is None or country is None:
        await callback_query.answer("Сообщение устарело")
        return
    await UserCollection(db).set_location(callback_query.from_user.id, location=country)
    await callback_query.answer(
        text=f"Супер. Установили для тебя страну {country}",
    )
