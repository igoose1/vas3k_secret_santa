import asyncio
import pathlib

from motor.motor_asyncio import AsyncIOMotorClient

from sesanta.bot import Bot
from sesanta.services.club_loader import ClubMemberLoader
from sesanta.settings import settings
from sesanta.utils.chat_auth import ChatAuthenticator


async def main() -> None:
    bot = Bot(
        settings.bot_token,
    )
    db_client = AsyncIOMotorClient(str(settings.mongo_uri))
    bot.add_dependency(
        "db",
        db_client[settings.mongo_db],
    )
    bot.add_dependency(
        "chat_authenticator",
        ChatAuthenticator(settings.secret, pathlib.Path("zstddict")),
    )
    bot.add_dependency(
        "club_member_loader",
        ClubMemberLoader(
            settings.club_by_telegram_id_endpoint,
            settings.club_token,
            settings.club_max_rate_per_minute,
        ),
    )
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
