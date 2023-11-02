from aiogram import Router

from sesanta.bot.handlers.authenticate import router as authenticate_router
from sesanta.bot.handlers.start import router as start_router

router = Router()
router.include_routers(
    start_router,
    authenticate_router,
)
