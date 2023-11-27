from aiogram.filters import Filter
from aiogram.types import Message

from sesanta.serving_status import ServingStatus
from sesanta.settings import settings


class ServingStatusFilter(Filter):
    def __init__(self, expected: ServingStatus):
        self.expected = expected

    async def __call__(self, message: Message) -> bool:
        return settings.serving_status == self.expected
