import pymongo

from sesanta.db.collections.messages import MessageCollection
from sesanta.db.collections.users import UserCollection
from sesanta.settings import settings

client = pymongo.MongoClient(str(settings.mongo_uri))
users = client[settings.mongo_db][UserCollection.name]
messages = client[settings.mongo_db][MessageCollection.name]
