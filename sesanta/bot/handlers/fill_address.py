from aiogram import F, Router
from aiogram.types import Message
from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.bot.filters import IsCompleteFilter
from sesanta.services.user_fill_address import UserAddressFiller

router = Router()


@router.message(F.text, IsCompleteFilter(is_completed=True))
async def handler(
    message: Message,
    db: AsyncIOMotorDatabase,
) -> None:
    address = message.text
    if address is None:
        msg = "never happens because of filters"
        raise NotImplementedError(msg)
    await UserAddressFiller(db)(
        telegram_id=message.chat.id,
        address=address,
    )
    await message.answer(f"Записали твои детали доставки!\n\n<pre>{address}</pre>")
