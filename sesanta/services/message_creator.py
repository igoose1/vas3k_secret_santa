import datetime

from aiogram import Bot as AiogramBot
from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.db.collections.messages import MessageCollection
from sesanta.db.collections.users import UserCollection
from sesanta.utils.chat_auth import ChatInfo


class MessageCreator:
    def __init__(self, db: AsyncIOMotorDatabase, bot: AiogramBot):
        self.users = UserCollection(db)
        self.messages = MessageCollection(db)
        self.bot = bot

    async def __call__(
        self,
        created_from_chat_info: ChatInfo,
        text: str,
        link_to_read: str,
    ) -> None:
        """Writes a new message and notifies a receiver in Telegram."""
        receiver_user = await self.users.get({"slug": created_from_chat_info.they})
        if receiver_user is None:
            msg = "user wasn't found in db"
            raise NotImplementedError(msg)

        await self.messages.new(
            sender=created_from_chat_info.me,
            receiver=created_from_chat_info.they,
            text=text,
            timestamp=datetime.datetime.now(datetime.UTC),
        )
        if created_from_chat_info.they == created_from_chat_info.santa:
            notify_text = [f"Новое сообщение от {created_from_chat_info.me}!"]
        else:
            notify_text = ["Новое сообщение от Санты!"]
        notify_text.append(
            f'➜ <a href="{link_to_read}">Просмотреть чат</a>',
        )
        notify_text.append(
            "<i>Никому не пересылайте это сообщение.</i>",
        )
        await self.bot.send_message(
            receiver_user.telegram_id,
            "\n\n".join(notify_text),
        )
