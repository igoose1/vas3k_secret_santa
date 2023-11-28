import asyncio

import asyncclick as click
from aiogram import Bot as AiogramBot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums.parse_mode import ParseMode
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from sesanta.db.collections.users import UserCollection
from sesanta.db.schemas.users import UserSchema
from sesanta.services.user_getter import UserGetter
from sesanta.settings import settings


async def generate_message_for(
    user: UserSchema,
    db: AsyncIOMotorDatabase,
) -> str:
    user_getter = UserGetter(db)
    if user.santa is None:
        msg = "can't generate for a user without santa"
        raise NotImplementedError(msg)
    if len(user.grandchildren) < 1:
        msg = "can't generate for a user without grandchildren"
        raise NotImplementedError(msg)
    paragraphs = []
    paragraphs.append(
        "Привет! Жеребьевка наконец свершилась.",
    )
    paragraphs.append(
        ("Начнем без предисловий. У тебя теперь есть личный санта!"),
    )
    paragraphs.append(
        (
            "А еще теперь ты санта! "
            "Пожалуйста, не забудь передать подарок (или подарки!) до 15 декабря. "
            "Это наш дедлайн. Если отправить позже, то получатель может не успеть "
            "забрать посылку до праздника."
        ),
    )
    for grandchild_slug in user.grandchildren:
        grandchild = await user_getter.must_exist(grandchild_slug)
        paragraphs.append(
            "Ты санта для клубчанина "
            f'<a href="https://vas3k.club/user/{grandchild.slug}/">'
            f"{grandchild.slug}</a>. "
            "Внимательно прочти профиль, комментарии и интро. Это поможет выбрать "
            "подходящий подарок",
        )
        paragraphs.append(
            f"В анкете {grandchild.slug} указана страна {grandchild.location}. "
            "У тебя отмечено, что ты можешь туда отправить подарок.",
        )
        if not grandchild.address:
            paragraphs.append(
                f"К сожалению, в анкете {grandchild.slug} не указан адрес. "
                "Придется узнавать его в чате.",
            )
        else:
            paragraphs.append(
                f"В анкете {grandchild.slug} указаны такие детали доставки:\n"
                f"<pre>{grandchild.address}</pre>",
            )
    paragraphs.append(
        "У нас есть чаты! Если хочешь написать от имени санты или связаться со своим "
        "сантой, напиши любое сообщение в боте. "
        "Тебе придут ссылки на специальную новогоднюю переписку.",
    )
    return "\n\n".join(paragraphs)


@click.command()
@click.option("--dry-run", default=False)
async def main(dry_run: bool) -> None:
    """Announce users from a database."""
    db = AsyncIOMotorClient(str(settings.mongo_uri))[settings.mongo_db]
    collection = UserCollection(db)
    async with AiohttpSession() as session:
        bot = AiogramBot(settings.bot_token, parse_mode=ParseMode.HTML, session=session)
        async for user in collection.get_all({"is_completed": True}):
            message = await generate_message_for(user, db)
            if dry_run:
                print(
                    f"Would send a message to {user.telegram_id} ({user.slug}):",
                    repr(message),
                )
                continue
            try:
                await bot.send_message(
                    user.telegram_id,
                    message,
                )
            except Exception as exc:
                print(f"{user}: {exc}")
            await asyncio.sleep(1 / 15)


if __name__ == "__main__":
    main(_anyio_backend="asyncio")
