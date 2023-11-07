from aiogram import Router

from sesanta.bot.handlers.complete import router as complete_router
from sesanta.bot.handlers.select_countries import router as select_countries_router
from sesanta.bot.handlers.set_location import router as set_location_router
from sesanta.bot.handlers.start import router as start_router

router = Router()
router.include_routers(
    start_router,
    set_location_router,
    select_countries_router,
    complete_router,
)
