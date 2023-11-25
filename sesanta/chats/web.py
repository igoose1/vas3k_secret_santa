import datetime
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from motor.motor_asyncio import AsyncIOMotorClient

from sesanta.db.collections.messages import MessageCollection
from sesanta.settings import settings
from sesanta.utils.chat_auth import ChatAuthenticator, ChatInfo, ExpiredError

db = AsyncIOMotorClient(str(settings.mongo_uri))[settings.mongo_db]
chat_authenticator = ChatAuthenticator(settings.secret)

app = FastAPI()


def get_chat_info(
    data: Annotated[str, Query(alias="d")],
) -> ChatInfo:
    try:
        return chat_authenticator(data)
    except ExpiredError:
        raise HTTPException(
            status.HTTP_401,
            "Ссылка истекла",
        )
    except ValueError:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Сюда нельзя",
        )


@app.get("/c/")
async def read_chat(
    request: Request,
    chat_info: ChatInfo = Depends(get_chat_info),
) -> str:
    messages = await MessageCollection(db).get_chat(chat_info.me, chat_info.they)
    return f"Чат {chat_info.sender} -> {chat_info.receiver}, сообщения: {messages}"


@app.post("/c/")
async def send_message(
    request: Request,
    text: str,
    chat_info: ChatInfo = Depends(get_chat_info),
) -> None:
    await MessageCollection(db).new(
        chat_info.me,
        chat_info.they,
        text,
        datetime.datetime.now(datetime.UTC),
    )
