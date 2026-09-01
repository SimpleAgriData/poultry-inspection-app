from fastapi import APIRouter

from app.api.v1.commands import (
    add_agricultural_holding_router,
    add_farm_router,
    add_section_router,
    delete_farm_router,
    delete_section_router,
    update_agricultural_holding_router,
    update_farm_router,
    update_section_router,
    import_stallkarte_router,
)
from app.api.v1.commands.stallkarte import (
    apply_pest_control_measures_router,
    assign_fattening_farm_router,
    assign_rearing_farm_router,
    clean_silo_router,
    delete_stallkarte_router,
    disinfect_stable_router,
    disinfect_water_line_router,
    finish_stallkarte_router,
    log_section_note_router,
    perform_alarm_test_router,
    perform_light_program_router,
    record_ambient_climate_router,
    record_fattening_day_data_router,
    record_feed_consumption_router,
    record_mortality_router,
    reopen_stallkarte_router,
    replace_installation_details_router,
    record_water_consumption_router,
    record_weight_router,
    revise_details_router,
    revise_transfer_details_router,
    save_finish_notes_router,
    save_general_notes_router,
    start_stallkarte_router,
    transfer_flock_router,
)
from app.api.v1.queries import (
    export_router,
    find_my_agricultural_holding_router,
    find_my_stallkarten_router,
    find_stallkarte_router,
    ping_router,
    status_router,
    chicken_breeds_router,
)

stallkarte_router = APIRouter()
stallkarte_router.include_router(start_stallkarte_router)
stallkarte_router.include_router(revise_details_router)
stallkarte_router.include_router(assign_fattening_farm_router)
stallkarte_router.include_router(assign_rearing_farm_router)
stallkarte_router.include_router(finish_stallkarte_router)
stallkarte_router.include_router(transfer_flock_router)
stallkarte_router.include_router(revise_transfer_details_router)
stallkarte_router.include_router(record_ambient_climate_router)
stallkarte_router.include_router(record_fattening_day_data_router)
stallkarte_router.include_router(record_feed_consumption_router)
stallkarte_router.include_router(save_general_notes_router)
stallkarte_router.include_router(save_finish_notes_router)
stallkarte_router.include_router(replace_installation_details_router)
stallkarte_router.include_router(record_mortality_router)
stallkarte_router.include_router(log_section_note_router)
stallkarte_router.include_router(record_water_consumption_router)
stallkarte_router.include_router(record_weight_router)
stallkarte_router.include_router(perform_alarm_test_router)
stallkarte_router.include_router(perform_light_program_router)
stallkarte_router.include_router(apply_pest_control_measures_router)
stallkarte_router.include_router(clean_silo_router)
stallkarte_router.include_router(reopen_stallkarte_router)
stallkarte_router.include_router(delete_stallkarte_router)
stallkarte_router.include_router(disinfect_stable_router)
stallkarte_router.include_router(disinfect_water_line_router)

commands_router = APIRouter()
commands_router.include_router(add_agricultural_holding_router)
commands_router.include_router(add_farm_router)
commands_router.include_router(add_section_router)
commands_router.include_router(update_agricultural_holding_router)
commands_router.include_router(update_farm_router)
commands_router.include_router(update_section_router)
commands_router.include_router(delete_farm_router)
commands_router.include_router(delete_section_router)
commands_router.include_router(import_stallkarte_router)
commands_router.include_router(
    stallkarte_router, prefix="/stallkarte", tags=["Stallkarte"]
)

queries_router = APIRouter()
queries_router.include_router(find_my_stallkarten_router)
queries_router.include_router(find_my_agricultural_holding_router)
queries_router.include_router(find_stallkarte_router)
queries_router.include_router(ping_router)
queries_router.include_router(status_router)
queries_router.include_router(export_router)
queries_router.include_router(chicken_breeds_router)

router = APIRouter(prefix="/api/v1")
router.include_router(commands_router, tags=["Commands"])
router.include_router(queries_router, tags=["Queries"])
