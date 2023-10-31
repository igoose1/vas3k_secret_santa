import abc

from motor.motor_asyncio import AsyncIOMotorDatabase


class AbstractCollection(abc.ABC):
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database[self.name]

    @property
    @abc.abstractmethod
    def name(self) -> str:
        ...
