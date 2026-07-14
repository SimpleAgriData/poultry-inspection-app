from .apply_pest_control_measures import router as apply_pest_control_measures_router
from .assign_fattening_farm import router as assign_fattening_farm_router
from .assign_rearing_farm import router as assign_rearing_farm_router
from .clean_silo import router as clean_silo_router
from .delete_stallkarte import router as delete_stallkarte_router
from .disinfect_stable import router as disinfect_stable_router
from .disinfect_water_line import router as disinfect_water_line_router
from .finish_stallkarte import router as finish_stallkarte_router
from .log_section_note import router as log_section_note_router
from .perform_alarm_test import router as perform_alarm_test_router
from .perform_light_program import router as perform_light_program_router
from .record_ambient_climate import router as record_ambient_climate_router
from .record_fattening_day_data import router as record_fattening_day_data_router
from .record_feed_consumption import router as record_feed_consumption_router
from .record_mortality import router as record_mortality_router
from .replace_installation_details import router as replace_installation_details_router
from .record_water_consumption import router as record_water_consumption_router
from .record_weight import router as record_weight_router
from .reopen_stallkarte import router as reopen_stallkarte_router
from .revise_details import router as revise_details_router
from .revise_transfer_details import router as revise_transfer_details_router
from .save_finish_notes import router as save_finish_notes_router
from .save_general_notes import router as save_general_notes_router
from .start_stallkarte import router as start_stallkarte_router
from .transfer_flock import router as transfer_flock_router

__all__ = [
    "apply_pest_control_measures_router",
    "assign_fattening_farm_router",
    "assign_rearing_farm_router",
    "clean_silo_router",
    "delete_stallkarte_router",
    "disinfect_stable_router",
    "disinfect_water_line_router",
    "finish_stallkarte_router",
    "log_section_note_router",
    "perform_alarm_test_router",
    "perform_light_program_router",
    "record_ambient_climate_router",
    "record_fattening_day_data_router",
    "record_feed_consumption_router",
    "record_mortality_router",
    "record_water_consumption_router",
    "record_weight_router",
    "reopen_stallkarte_router",
    "replace_installation_details_router",
    "revise_details_router",
    "revise_transfer_details_router",
    "save_finish_notes_router",
    "save_general_notes_router",
    "start_stallkarte_router",
    "transfer_flock_router",
]
