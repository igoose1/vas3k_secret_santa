import typing

from aiogram import Router
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.bot.filters.eligible import IsEligibleFilter
from sesanta.bot.filters.serving_status import ServingStatusFilter
from sesanta.db.collections.users import UserCollection
from sesanta.services.country_chooser import COUNTRIES, HASH_TO_COUNTRY, hash_country
from sesanta.services.user_getter import UserGetter
from sesanta.serving_status import ServingStatus

router = Router()


class SetLocationCallback(CallbackData, prefix="sl"):
    country_hash: str
    offset: int

    @classmethod
    def from_country(cls, country: str, offset: int) -> typing.Self:
        return cls(country_hash=hash_country(country), offset=offset)

    @property
    def country(self) -> str | None:
        return HASH_TO_COUNTRY.get(self.country_hash)


class SetLocationPagerCallback(CallbackData, prefix="slp"):
    offset: int


BUTTONS_IN_ONE_KEYBOARD = 20


def generate_set_location_keyboard(
    offset: int,
    already_set: str | None,
) -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()
    for country in COUNTRIES[offset : offset + BUTTONS_IN_ONE_KEYBOARD]:
        text = ("✅ " if already_set == country else "") + country
        keyboard_builder.button(
            text=text,
            callback_data=SetLocationCallback.from_country(country, offset),
        )
    if offset:
        keyboard_builder.button(
            text="⬅️",
            callback_data=SetLocationPagerCallback(
                offset=max(0, offset - BUTTONS_IN_ONE_KEYBOARD),
            ),
        )
    if offset + BUTTONS_IN_ONE_KEYBOARD < len(COUNTRIES):
        keyboard_builder.button(
            text="➡️",
            callback_data=SetLocationPagerCallback(
                offset=offset + BUTTONS_IN_ONE_KEYBOARD,
            ),
        )
    keyboard_builder.adjust(2)
    return keyboard_builder.as_markup()


@router.callback_query(SetLocationPagerCallback.filter(), IsEligibleFilter())
async def pager_handler(
    callback_query: CallbackQuery,
    callback_data: SetLocationPagerCallback,
    db: AsyncIOMotorDatabase,
) -> None:
    if callback_query.message is None:
        await callback_query.answer("Кнопки устарели, перезапусти их через /start")
        return
    user = await UserGetter(db).must_exist(callback_query.from_user.id)
    await callback_query.message.edit_reply_markup(
        reply_markup=generate_set_location_keyboard(
            callback_data.offset,
            already_set=user.location,
        ),
    )


@router.callback_query(
    SetLocationCallback.filter(),
    IsEligibleFilter(),
    ServingStatusFilter(ServingStatus.COLLECTING_FORMS),
)
async def callback_handler(
    callback_query: CallbackQuery,
    callback_data: SetLocationCallback,
    db: AsyncIOMotorDatabase,
) -> None:
    country = callback_data.country
    if callback_query.message is None or country is None:
        await callback_query.answer("Кнопки устарели, перезапусти их через /start")
        return
    user = await UserGetter(db).must_exist(callback_query.from_user.id)
    if user.is_completed:
        await callback_query.answer(
            "Анкета уже отмечена завершенной. Перезапусти ее через /start.",
        )
        return
    await UserCollection(db).set_location(callback_query.from_user.id, location=country)
    await callback_query.message.edit_reply_markup(
        reply_markup=generate_set_location_keyboard(
            offset=callback_data.offset,
            already_set=country,
        ),
    )
