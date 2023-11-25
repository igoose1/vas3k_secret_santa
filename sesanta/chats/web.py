import datetime
from typing import Annotated

from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.templating import _TemplateResponse

from sesanta.db.collections.messages import MessageCollection
from sesanta.settings import settings
from sesanta.utils.chat_auth import ChatAuthenticator, ChatInfo, ExpiredError

db = AsyncIOMotorClient(str(settings.mongo_uri))[settings.mongo_db]
chat_authenticator = ChatAuthenticator(settings.secret)
templates = Jinja2Templates("sesanta/chats/templates")

app = FastAPI()


def get_chat_info(
    data: str,
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
    await MessageCollection(db).new(
        chat_info.me,
        chat_info.they,
        text,
        datetime.datetime.now(datetime.UTC),
    )
    return RedirectResponse(
        request.url_for("read_chat", data=data),
        status.HTTP_303_SEE_OTHER,
    )
