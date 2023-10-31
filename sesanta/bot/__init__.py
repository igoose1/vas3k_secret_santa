from aiogram import Bot as AiogramBot
from aiogram import Dispatcher

from sesanta.bot.handlers import start_router


class Bot:
    def __init__(self, token: str) -> None:
        self.bot = AiogramBot(token)
        self.dispatcher = Dispatcher()
        self.populate_handlers()

    def populate_handlers(self) -> None:
        self.dispatcher.include_routers(
            start_router,
        )

    async def start(self) -> None:
        await self.dispatcher.start_polling(self.bot)
