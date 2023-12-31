from aiogram import Router

from sesanta.bot.handlers.complete import router as complete_router
from sesanta.bot.handlers.delete import router as delete_router
from sesanta.bot.handlers.fill_address import router as fill_address_router
from sesanta.bot.handlers.get_chats import router as get_chats_router
from sesanta.bot.handlers.select_countries import router as select_countries_router
from sesanta.bot.handlers.set_delivery_status import (
    router as set_delivery_status_router,
)
from sesanta.bot.handlers.set_location import router as set_location_router
from sesanta.bot.handlers.start import router as start_router
from sesanta.bot.handlers.understood_select_countries import (
    router as understood_select_countries_router,
)
from sesanta.bot.handlers.understood_set_location import (
    router as understood_set_location_router,
)
from sesanta.bot.handlers.wait_for_drawing import router as wait_for_drawing_router

router = Router()
router.include_routers(
    wait_for_drawing_router,
    set_delivery_status_router,
    get_chats_router,  # this is almost unfiltered, be careful with its order
    start_router,
    set_location_router,
    select_countries_router,
    complete_router,
    understood_set_location_router,
    understood_select_countries_router,
    delete_router,
    fill_address_router,
)
