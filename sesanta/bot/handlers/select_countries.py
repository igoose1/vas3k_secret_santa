import typing

from aiogram import Router
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.db.collections.users import UserCollection
from sesanta.services.country_chooser import COUNTRIES, HASH_TO_COUNTRY, hash_country
from sesanta.services.user_getter import UserGetter

router = Router(name="select_countries")


class SelectCountriesCallback(CallbackData, prefix="sc"):
    country_hash: str
    to_mark: bool
    offset: int

    @classmethod
    def from_country(cls, country: str, to_mark: bool, offset: int) -> typing.Self:
        return cls(country_hash=hash_country(country), to_mark=to_mark, offset=offset)

    @property
    def country(self) -> str | None:
        return HASH_TO_COUNTRY.get(self.country_hash)


class SelectCountriesPagerCallback(CallbackData, prefix="scp"):
    offset: int


COUNTRIES_IN_ONE_KEYBOARD = 16


def generate_select_countries_keyboard(
    offset: int,
    already_selected: set[str],
) -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()
    for country in COUNTRIES[offset : offset + COUNTRIES_IN_ONE_KEYBOARD]:
        text = ("✔️ " if country in already_selected else "") + country
        keyboard_builder.button(
            text=text,
            callback_data=SelectCountriesCallback.from_country(
                country,
                to_mark=country not in already_selected,
                offset=offset,
            ),
        )
    if offset:
        keyboard_builder.button(
            text="⬅️",
            callback_data=SelectCountriesPagerCallback(
                offset=offset - COUNTRIES_IN_ONE_KEYBOARD,
            ),
        )
    if offset + COUNTRIES_IN_ONE_KEYBOARD < len(COUNTRIES):
        keyboard_builder.button(
            text="➡️",
            callback_data=SelectCountriesPagerCallback(
                offset=offset + COUNTRIES_IN_ONE_KEYBOARD,
            ),
        )
    keyboard_builder.adjust(2)
    return keyboard_builder.as_markup()


@router.callback_query(SelectCountriesPagerCallback.filter())
async def pager_handler(
    callback_query: CallbackQuery,
    callback_data: SelectCountriesPagerCallback,
    db: AsyncIOMotorDatabase,
) -> None:
    if callback_query.message is None:
        await callback_query.answer("Сообщение устарело")
        return
    user = await UserGetter(db)(callback_query.from_user.id)
    if user is None:
        msg = "never happens"
        raise NotImplementedError(msg)
    await callback_query.message.edit_reply_markup(
        reply_markup=generate_select_countries_keyboard(
            callback_data.offset,
            already_selected=user.selected_countries,
        ),
    )


@router.callback_query(SelectCountriesCallback.filter())
async def callback_handler(
    callback_query: CallbackQuery,
    callback_data: SelectCountriesCallback,
    db: AsyncIOMotorDatabase,
) -> None:
    country = callback_data.country
    if callback_query.message is None or country is None:
        await callback_query.answer("Сообщение устарело")
        return
    if callback_data.to_mark:
        await UserCollection(db).select_country(
            callback_query.from_user.id,
            country=country,
        )
    else:
        await UserCollection(db).unselect_country(
            callback_query.from_user.id,
            country=country,
        )
    user = await UserGetter(db)(callback_query.from_user.id)
    if user is None:
        msg = "never happens"
        raise NotImplementedError(msg)
    await callback_query.message.edit_reply_markup(
        reply_markup=generate_select_countries_keyboard(
            callback_data.offset,
            already_selected=user.selected_countries,
        ),
    )
