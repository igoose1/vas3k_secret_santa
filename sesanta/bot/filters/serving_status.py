from aiogram.filters import Filter
from aiogram.types import Message

from sesanta.settings import ServingStatus, settings


class ServingStatusFilter(Filter):
    def __init__(self, expected: ServingStatus):
        self.expected = expected

    async def __call__(self, message: Message) -> bool:
        return settings.serving_status == self.expected
