from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


class Mongo:
    def __init__(self, uri: str, database_name: str):
        self.client = AsyncIOMotorClient(uri)
        self.database_name = database_name

    @property
    def db(self) -> AsyncIOMotorDatabase:
        return self.client[self.database_name]
