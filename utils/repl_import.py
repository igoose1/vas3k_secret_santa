import pymongo

from sesanta.db.collections.users import UserCollection
from sesanta.settings import settings

client = pymongo.MongoClient(str(settings.mongo_uri))
collection = col = client[settings.mongo_db][UserCollection.name]
