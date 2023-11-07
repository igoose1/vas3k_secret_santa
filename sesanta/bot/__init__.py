import typing

from aiogram import Bot as AiogramBot
from aiogram import Dispatcher
from aiogram.enums.parse_mode import ParseMode

from sesanta.bot.handlers import router


class Bot:
    def __init__(self, token: str) -> None:
        self.bot = AiogramBot(token, parse_mode=ParseMode.HTML)
        self.dispatcher = Dispatcher()
        self.populate_handlers()

    def populate_handlers(self) -> None:
        self.dispatcher.include_router(router)

    def add_dependency(self, name: str, dependency: typing.Any) -> None:
        self.dispatcher[name] = dependency

    async def start(self) -> None:
        await self.dispatcher.start_polling(self.bot)
