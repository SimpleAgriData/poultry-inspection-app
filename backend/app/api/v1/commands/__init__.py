from .add_agricultural_holding import router as add_agricultural_holding_router
from .add_farm import router as add_farm_router
from .add_section import router as add_section_router
from .delete_farm import router as delete_farm_router
from .delete_section import router as delete_section_router
from .update_agricultural_holding import router as update_agricultural_holding_router
from .update_farm import router as update_farm_router
from .update_section import router as update_section_router
from .import_stallkarte import router as import_stallkarte_router

__all__ = [
    "add_agricultural_holding_router",
    "add_farm_router",
    "add_section_router",
    "delete_farm_router",
    "delete_section_router",
    "import_stallkarte_router",
    "update_agricultural_holding_router",
    "update_farm_router",
    "update_section_router",
]
