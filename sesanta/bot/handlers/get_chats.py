from aiogram import Router
from aiogram.types import Message
from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.bot.filters.serving_status import ServingStatusFilter
from sesanta.services.user_getter import UserGetter
from sesanta.serving_status import ServingStatus
from sesanta.settings import settings
from sesanta.utils.chat_auth import ChatAuthenticator

router = Router()


@router.message(ServingStatusFilter(ServingStatus.SENDING_GIFTS))
async def handler(
    message: Message,
    db: AsyncIOMotorDatabase,
    chat_authenticator: ChatAuthenticator,
) -> None:
    user = await UserGetter(db)(message.chat.id)
    if user is None:
        await message.answer("Не нашел тебя в базе.")
        return
    if user.santa is None:
        await message.answer(
            "Тебе не был распределен санта. "
            "Скорее всего, твоя анкета не была завершена.\n\n"
            f"Думаешь, это ошибка? Отпишись под постом: {settings.club_post_link}",
        )
        return
    paragraphs = []
    with_santa = settings.chats_full_url_for(
        chat_authenticator.generate(
            user.slug,
            user.santa,
            santa=user.santa,
            expire_in=settings.chats_expire_in,
        ),
    )
    paragraphs.append(
        f'Ссылка для <a href="{with_santa}">чата с Сантой</a>.',
    )
    for grandchild in user.grandchildren:
        with_grandchild = settings.chats_full_url_for(
            chat_authenticator.generate(
                user.slug,
                grandchild,
                santa=user.slug,
                expire_in=settings.chats_expire_in,
            ),
        )
        paragraphs.append(
            f'Ссылка для <a href="{with_grandchild}">чата с {grandchild}</a>.',
        )

    paragraphs.append(
        "Не делитесь этим сообщением. Чтобы было безопаснее, эти ссылки временные. "
        "Чтобы получить новые, просто отправьте еще одно сообщение боту.",
    )
    await message.answer(
        "\n\n".join(paragraphs),
    )
