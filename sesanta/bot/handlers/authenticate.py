from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from motor.motor_asyncio import AsyncIOMotorDatabase

from sesanta.bot.filters import IsAuthenticatedFilter
from sesanta.services.user_eligibility_setter import UserEligibilitySetter
from sesanta.services.user_is_eligible import IsUserEligible

router = Router(name="authenticate")


@router.message(Command("auth"), IsAuthenticatedFilter())
async def handler(
    message: Message,
    db: AsyncIOMotorDatabase,
) -> None:
    passed_criteria = await IsUserEligible(db).check_criteria(message.chat.id)
    if passed_criteria:
        await message.reply("Подходишь по критериям!")
        await UserEligibilitySetter(db).users.set_eligibility(
            message.chat.id,
            is_eligible=True,
        )
    else:
        await message.reply("He подходишь!")
