import asyncio
import pathlib
import sys

import asyncclick as click
import hjson
from aiogram import Bot as AiogramBot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums.parse_mode import ParseMode
from pydantic import TypeAdapter

from sesanta.settings import settings
from utils.basic import User

UserListAdapter = TypeAdapter(list[User])


@click.command()
@click.option("--dry-run", default=False)
@click.argument("message")
async def main(message: str, dry_run: bool) -> None:
    """Send a message to users from stdin."""
    message_path = pathlib.Path(message)
    del message
    message_content = message_path.read_text()

    async with AiohttpSession() as session:
        bot = AiogramBot(settings.bot_token, parse_mode=ParseMode.HTML, session=session)

        users = UserListAdapter.validate_python(hjson.load(sys.stdin))
        for user in users:
            if dry_run:
                print(f"Would send a message to {user.telegram_id} ({user.slug})")
                continue
            try:
                await bot.send_message(
                    user.telegram_id,
                    message_content,
                )
            except Exception as exc:
                print(f"{user}: {exc}")
            await asyncio.sleep(1 / 15)


if __name__ == "__main__":
    main(_anyio_backend="asyncio")
