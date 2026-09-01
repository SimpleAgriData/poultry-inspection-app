from .export_stallkarte import router as export_router
from .find_my_agricultural_holding import router as find_my_agricultural_holding_router
from .find_my_stallkarten import router as find_my_stallkarten_router
from .find_stallkarte import router as find_stallkarte_router
from .ping import router as ping_router
from .status import router as status_router
from .get_chicken_breeds import router as chicken_breeds_router

__all__ = [
    "export_router",
    "find_my_agricultural_holding_router",
    "find_my_stallkarten_router",
    "find_stallkarte_router",
    "ping_router",
    "status_router",
    "chicken_breeds_router",
]
