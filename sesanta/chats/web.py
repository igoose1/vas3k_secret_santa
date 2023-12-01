import pathlib
from typing import Annotated

from aiogram import Bot as AiogramBot
from aiogram.enums.parse_mode import ParseMode
from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.templating import _TemplateResponse

from sesanta.db.collections.messages import MessageCollection
from sesanta.services.message_creator import MessageCreator
from sesanta.settings import settings
from sesanta.utils.chat_auth import ChatAuthenticator, ChatData, ChatInfo, ExpiredError

db = AsyncIOMotorClient(str(settings.mongo_uri))[settings.mongo_db]
chat_authenticator = ChatAuthenticator(settings.secret, pathlib.Path("zstddict"))
templates = Jinja2Templates("sesanta/chats/templates")
bot = AiogramBot(settings.bot_token, parse_mode=ParseMode.HTML)

app = FastAPI()


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> _TemplateResponse:
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "detail": exc.detail,
        },
        status_code=exc.status_code,
    )


def get_chat_info(
    data: ChatData,
) -> ChatInfo:
    try:
        return chat_authenticator(data)
    except ExpiredError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Ссылка истекла. Напиши боту любое сообщение и получи новую.",
        )
    except ValueError:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Сюда нельзя. Напиши боту любое сообщение и получи правильную ссылку.",
        )


@app.get("/c/{data}/", response_class=HTMLResponse)
async def read_chat(
    request: Request,
    chat_info: ChatInfo = Depends(get_chat_info),
) -> _TemplateResponse:
    messages = await MessageCollection(db).get_chat(chat_info.me, chat_info.they)
    return templates.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "messages": messages,
            "santa": chat_info.santa,
            "grandchild": chat_info.grandchild,
            "me": chat_info.me,
        },
    )


@app.post("/c/{data}/")
async def send_message(
    request: Request,
    data: str,
    text: Annotated[str, Form()],
    chat_info: ChatInfo = Depends(get_chat_info),
) -> RedirectResponse:
    receiver_data = chat_authenticator.generate(
        sender=chat_info.receiver,
        receiver=chat_info.sender,  # they aren't messed
        santa=chat_info.santa,
        expire_in=settings.chats_expire_in,
    )
    url = request.url_for("read_chat", data=receiver_data)
    await MessageCreator(db, bot)(
        chat_info,
        text,
        str(url),
    )
    return RedirectResponse(
        request.url_for("read_chat", data=data),
        status.HTTP_303_SEE_OTHER,
    )
