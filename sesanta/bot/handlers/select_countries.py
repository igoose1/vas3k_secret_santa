import typing

from aiogram import Router
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.bot.filters.eligible import IsEligibleFilter
from sesanta.db.collections.users import UserCollection
from sesanta.services.country_chooser import (
    COUNTRIES,
    GROUPS,
    HASH_TO_COUNTRY,
    hash_country,
)
from sesanta.services.user_getter import UserGetter
from sesanta.utils.emoji import random_cool_emoji
from sesanta.utils.plural import RuPlural

router = Router()


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


class SelectGroupCallback(CallbackData, prefix="sg"):
    group_name: str
    offset: int

    @property
    def countries(self) -> list[str]:
        return GROUPS.get(self.group_name, [])


class SelectCountriesPagerCallback(CallbackData, prefix="scp"):
    offset: int


BUTTONS_IN_ONE_KEYBOARD = 16


def generate_select_countries_keyboard(
    offset: int,
    already_selected: set[str],
) -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()
    for group_name in list(GROUPS)[offset : offset + BUTTONS_IN_ONE_KEYBOARD]:
        plural = RuPlural("страна", "страны", "стран")
        length = len(GROUPS[group_name])
        emoji = random_cool_emoji()  # to avoid "Bad Request: message is not modified"
        text = f"{emoji} {group_name} ({length} {plural(length)})"
        keyboard_builder.button(
            text=text,
            callback_data=SelectGroupCallback(
                group_name=group_name,
                offset=offset,
            ),
        )
    coffset = max(0, offset - len(GROUPS))
    climit = coffset + BUTTONS_IN_ONE_KEYBOARD - len(GROUPS)
    for country in COUNTRIES[coffset:climit]:
        text = ("✅ " if country in already_selected else "") + country
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
                offset=offset - BUTTONS_IN_ONE_KEYBOARD,
            ),
        )
    if offset + BUTTONS_IN_ONE_KEYBOARD < len(COUNTRIES):
        keyboard_builder.button(
            text="➡️",
            callback_data=SelectCountriesPagerCallback(
                offset=offset + BUTTONS_IN_ONE_KEYBOARD,
            ),
        )
    keyboard_builder.adjust(2)
    return keyboard_builder.as_markup()


@router.callback_query(SelectCountriesPagerCallback.filter(), IsEligibleFilter())
async def pager_handler(
    callback_query: CallbackQuery,
    callback_data: SelectCountriesPagerCallback,
    db: AsyncIOMotorDatabase,
) -> None:
    if callback_query.message is None:
        await callback_query.answer("Сообщение устарело")
        return
    user = await UserGetter(db).must_exist(callback_query.from_user.id)
    await callback_query.message.edit_reply_markup(
        reply_markup=generate_select_countries_keyboard(
            callback_data.offset,
            already_selected=user.selected_countries,
        ),
    )


@router.callback_query(SelectCountriesCallback.filter(), IsEligibleFilter())
async def callback_handler(
    callback_query: CallbackQuery,
    callback_data: SelectCountriesCallback,
    db: AsyncIOMotorDatabase,
) -> None:
    country = callback_data.country
    if callback_query.message is None or country is None:
        await callback_query.answer("Сообщение устарело")
        return
    user = await UserGetter(db).must_exist(callback_query.from_user.id)
    if user.is_complete:
        await callback_query.answer("Анкета уже была отмечена завершенной.")
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
    # update to get new selected countries
    user = await UserGetter(db).must_exist(callback_query.from_user.id)
    await callback_query.message.edit_reply_markup(
        reply_markup=generate_select_countries_keyboard(
            callback_data.offset,
            already_selected=user.selected_countries,
        ),
    )


@router.callback_query(SelectGroupCallback.filter(), IsEligibleFilter())
async def group_handler(
    callback_query: CallbackQuery,
    callback_data: SelectGroupCallback,
    db: AsyncIOMotorDatabase,
) -> None:
    if callback_query.message is None:
        await callback_query.answer("Сообщение устарело")
        return
    user = await UserGetter(db).must_exist(callback_query.from_user.id)
    if user.is_complete:
        await callback_query.answer("Анкета уже была отмечена завершенной.")
        return
    await UserCollection(db).select_countries(
        callback_query.from_user.id,
        countries=callback_data.countries,
    )
    # update to get new selected countries
    user = await UserGetter(db).must_exist(callback_query.from_user.id)
    await callback_query.message.edit_reply_markup(
        reply_markup=generate_select_countries_keyboard(
            callback_data.offset,
            already_selected=user.selected_countries,
        ),
    )
