from pydantic import BaseModel


class StallkarteHoldingMapping(BaseModel):
    holding_name: str
    holding_address: str
    fattening_cycle: str
    rearing_farm_name: str
    rearing_farm_vvvo_number: str
    rearing_barn_number: str
    fattening_farm_name: str
    fattening_farm_vvvo_number: str
    fattening_barn_number: str
    date_hatched: str
    animals_count: str
    date_transferred: str
    hatchery_name: str
    breed: str
    production_week: str
    eco_control_number: str
    parent_flock: str
    eu_bio: str
    naturland: str


default_stallkarte_holding_mapping = StallkarteHoldingMapping(
    holding_name="B1",
    holding_address="I1",
    fattening_cycle="O1",
    rearing_farm_name="B2",
    rearing_barn_number="I2",
    rearing_farm_vvvo_number="O2",
    fattening_farm_name="B3",
    fattening_barn_number="I3",
    fattening_farm_vvvo_number="O3",
    date_hatched="B4",
    animals_count="I4",
    date_transferred="O4",
    hatchery_name="B5",
    breed="I5",
    production_week="O5",
    eco_control_number="B6",
    parent_flock="I6",
    eu_bio="P6",
    naturland="Q6",
)


class YesNoMapping(BaseModel):
    yes: str
    no: str


class StallkarteChecklistMapping(BaseModel):
    did_emergency_power_test: YesNoMapping
    did_alarm_test: YesNoMapping

    did_dark_period_test: YesNoMapping
    had_deviations_due_to_vet: YesNoMapping

    stable_disinfection_date: str
    stable_disinfectant: str
    stable_disinfectant_dosis: str

    silo_cleaning_date: str
    silo_detergent: str
    silo_detergent_dosis: str

    water_line_disinfection_date: str
    water_line_disinfectant: str
    water_line_disinfectant_dosis: str

    did_pest_control_measures: YesNoMapping
    pest_control_measures_annotation: str


default_stallkarte_checklist_mapping = StallkarteChecklistMapping(
    did_emergency_power_test=YesNoMapping(yes="C8", no="D8"),
    did_alarm_test=YesNoMapping(yes="C9", no="D9"),
    did_dark_period_test=YesNoMapping(yes="J8", no="K8"),
    had_deviations_due_to_vet=YesNoMapping(yes="J9", no="K9"),
    stable_disinfection_date="O8",
    stable_disinfectant="P8",
    stable_disinfectant_dosis="Q8",
    silo_cleaning_date="O9",
    silo_detergent="P9",
    silo_detergent_dosis="Q9",
    water_line_disinfection_date="O10",
    water_line_disinfectant="P10",
    water_line_disinfectant_dosis="Q10",
    did_pest_control_measures=YesNoMapping(yes="G10", no="H10"),
    pest_control_measures_annotation="K10",
)


class StallkarteProductionDayMapping(BaseModel):
    day: str
    natural_mortality: str
    selective_mortality: str
    weight: str
    did_inspection_1: str
    did_inspection_2: str
    temperature: str
    humidity: str
    water_consumption: str
    feed_consumption: str
    annotation: str


class StallkarteProductionDaysMapping(BaseModel):
    date: str
    day: str
    natural_mortality: str
    selective_mortality: str
    cumulative_mortality: str
    weight: str
    did_inspection_1: str
    did_inspection_2: str
    temperature: str
    humidity: str
    water_consumption: str
    feed_consumption: str
    annotation: str
    start_row: int
    end_row: int
    skipped_rows: list[int]
    fattening_start_row: int


default_stallkarte_production_days_mapping = StallkarteProductionDaysMapping(
    date="A",
    day="B",
    natural_mortality="C",
    selective_mortality="D",
    cumulative_mortality="F",
    weight="H",
    did_inspection_1="I",
    did_inspection_2="J",
    temperature="K",
    humidity="L",
    water_consumption="M",
    feed_consumption="O",
    annotation="Q",
    start_row=15,
    end_row=87,
    skipped_rows=[
        23,  # "Qualitätsbericht Bio-Küken"
        56,  # "Sockenprobe 1"
        64,  # "Sockenprobe 2"
    ],
    fattening_start_row=51,
)


class ThroughputReportHeaderMapping(BaseModel):
    farm_number_cell: str
    holding_name_cell: str
    holding_address_cell: str
    fattening_cycle_cell: str
    fattening_farm_name_cell: str
    fattening_stalls_cell: str
    fattening_vvvo_number_cell: str
    rearing_farm_name_cell: str
    rearing_stalls_cell: str
    rearing_vvvo_number_cell: str
    date_hatched_cell: str
    transfer_date_cell: str
    hatchery_cell: str
    breed_cell: str
    production_week_cell_primary: str
    production_week_cell_secondary: str
    production_week_cell_tertiary: str
    eco_control_number_cell: str
    parent_flock_cell_primary: str
    parent_flock_cell_secondary: str
    parent_flock_cell_tertiary: str
    bedding_cell: str
    eu_bio_cell: str
    naturland_cell: str


default_throughput_report_header_mapping = ThroughputReportHeaderMapping(
    farm_number_cell="M2",
    holding_name_cell="B4",
    holding_address_cell="D4",
    fattening_cycle_cell="L4",
    fattening_farm_name_cell="B5",
    fattening_stalls_cell="D5",
    fattening_vvvo_number_cell="H5",
    rearing_farm_name_cell="B6",
    rearing_stalls_cell="D6",
    rearing_vvvo_number_cell="H6",
    date_hatched_cell="B7",
    transfer_date_cell="H7",
    hatchery_cell="B8",
    breed_cell="D8",
    production_week_cell_primary="H8",
    production_week_cell_secondary="J8",
    production_week_cell_tertiary="L8",
    eco_control_number_cell="B9",
    parent_flock_cell_primary="D9",
    parent_flock_cell_secondary="E9",
    parent_flock_cell_tertiary="F9",
    bedding_cell="B41",
    eu_bio_cell="H9",
    naturland_cell="L9",
)


class ThroughputReportMortalityMapping(BaseModel):
    rearing_column: str
    fattening_column: str
    first_day_row: int
    total_animals_cell: str


default_throughput_report_mortality_mapping = ThroughputReportMortalityMapping(
    rearing_column="I",
    fattening_column="L",
    first_day_row=12,
    total_animals_cell="D7",
)


class ThroughputReportFinishNotesMapping(BaseModel):
    slaughter_rows: tuple[int, int, int]
    slaughter_date_column: str
    slaughter_animals_count_column: str
    slaughter_slaughterer_column: str
    catching_date_cells: tuple[str, str, str]
    catching_catcher_cells: tuple[str, str, str]
    catching_time_cells: tuple[str, str, str]


default_throughput_report_finish_notes_mapping = ThroughputReportFinishNotesMapping(
    slaughter_rows=(11, 12, 13),
    slaughter_date_column="B",
    slaughter_animals_count_column="C",
    slaughter_slaughterer_column="E",
    catching_date_cells=("B37", "C37", "D37"),
    catching_catcher_cells=("B38", "C38", "D38"),
    catching_time_cells=("B39", "C39", "D39"),
)


class ThroughputReportGeneralNotesMapping(BaseModel):
    vaccination_rows: tuple[int, ...]
    vaccination_delivery_receipt_column: str
    vaccination_batch_number_column: str
    vaccination_code_column: str
    vaccination_date_column: str
    treatment_rows: tuple[int, ...]
    treatment_delivery_receipt_column: str
    treatment_treatment_code_column: str
    treatment_amount_column: str
    treatment_batch_number_column: str
    treatment_start_date_column: str
    treatment_end_date_column: str
    treatment_waiting_time_column: str
    sock_test_result: YesNoMapping
    sock_test_date: str


default_throughput_report_general_notes_mapping = ThroughputReportGeneralNotesMapping(
    vaccination_rows=(21, 22, 23, 24, 25, 26),
    vaccination_delivery_receipt_column="A",
    vaccination_batch_number_column="B",
    vaccination_code_column="C",
    vaccination_date_column="G",
    treatment_rows=(30, 31, 32),
    treatment_delivery_receipt_column="A",
    treatment_treatment_code_column="B",
    treatment_amount_column="C",
    treatment_batch_number_column="D",
    treatment_start_date_column="E",
    treatment_end_date_column="F",
    treatment_waiting_time_column="G",
    sock_test_result= YesNoMapping(yes="C34", no="C35"),
    sock_test_date= "D33"
)


class QualityReportBioChicksMapping(BaseModel):
    holding_name_cell: str
    holding_address_cell: str
    farm_name_cell: str
    farm_section_cellwidth: int
    farm_section_name_column_start: str
    farm_section_name_row: int
    parent_flock_column_start: str
    parent_flock_row: int
    production_week_column_start: str
    production_week_row: int
    date_hatched_cell: str
    hatchery_cell: str
    animals_count_cell: str
    mortality_first_row: int
    mortality_last_row: int
    template_first_row: int
    summary_row: int
    stall_heading_row: int
    stall_heading_prefix: str
    stall_subheading_row: int
    stall_columns: tuple[tuple[str, str, str], ...]
    avg_weight_day_7_column: str
    avg_weight_day_7_label_column: str
    avg_weight_day_7_template_row: int


default_quality_report_bio_chicks_mapping = QualityReportBioChicksMapping(
    holding_name_cell="B3",
    holding_address_cell="B5",
    farm_name_cell="B7",
    farm_section_cellwidth=3,
    farm_section_name_column_start="B",
    farm_section_name_row=8,
    parent_flock_column_start="B",
    parent_flock_row=9,
    production_week_column_start="B",
    production_week_row=10,
    date_hatched_cell="B11",
    hatchery_cell="C14",
    animals_count_cell="C15",
    mortality_first_row=19,
    mortality_last_row=26,
    template_first_row=15,
    summary_row=27,
    stall_heading_row=17,
    stall_heading_prefix="Stall",
    stall_subheading_row=18,
    stall_columns=(("B", "C", "D"), ("E", "F", "G"), ("H", "I", "J")),
    avg_weight_day_7_column="F",
    avg_weight_day_7_label_column="A",
    avg_weight_day_7_template_row=30,
)


class ExportWorksheetNames(BaseModel):
    section_template_name: str
    section_title_prefix: str
    throughput_report_name: str
    quality_report_bio_chicks_name: str
    outdoor_journal_name: str


default_export_worksheet_names = ExportWorksheetNames(
    section_template_name="Stallkarte TEMPLATE",
    section_title_prefix="Stallkarte",
    throughput_report_name="Durchgangsbericht",
    quality_report_bio_chicks_name="Qualitätsbericht Bio-Küken",
    outdoor_journal_name="Auslaufjournal",
)


class OutdoorJournalHeaderMapping(BaseModel):
    fattening_cycle_cell: str
    holding_name_cell: str
    fattening_farm_name_cell: str
    holding_address_cell: str
    rearing_farm_name_cell: str
    stall_cell: str
    parent_flock_cell: str
    production_week_cell: str
    date_hatched_cell: str
    transfer_date_cell: str
    clear_cells: tuple[str, ...]


default_outdoor_journal_header_mapping = OutdoorJournalHeaderMapping(
    fattening_cycle_cell="K3",
    holding_name_cell="B4",
    fattening_farm_name_cell="I4",
    holding_address_cell="B5",
    rearing_farm_name_cell="I5",
    stall_cell="A7",
    parent_flock_cell="B7",
    production_week_cell="F7",
    date_hatched_cell="I7",
    transfer_date_cell="K7",
    clear_cells=(),
)


class OutdoorJournalDaysMapping(BaseModel):
    first_data_row: int
    date_column: str
    opening_time_column: str
    sun_column: str
    cloudy_column: str
    precipitation_column: str
    extreme_wetness_column: str
    frost_column: str
    strong_wind_column: str
    veterinarian_column: str
    default_data_row_count: int
    summary_row: int
    summary_total_cell_column: str


default_outdoor_journal_days_mapping = OutdoorJournalDaysMapping(
    first_data_row=10,
    date_column="A",
    opening_time_column="B",
    sun_column="C",
    cloudy_column="E",
    precipitation_column="F",
    extreme_wetness_column="G",
    frost_column="H",
    strong_wind_column="I",
    veterinarian_column="J",
    default_data_row_count=1,
    summary_row=12,
    summary_total_cell_column="G",
)


def _calculate_row_by_production_day() -> dict[int, int]:
    row_by_production_day: dict[int, int] = {}

    production_day = 0

    cfg = default_stallkarte_production_days_mapping

    for row_number in range(cfg.start_row, cfg.end_row + 1):
        if row_number not in cfg.skipped_rows:
            row_by_production_day[production_day] = row_number
            production_day += 1

    return row_by_production_day


ROW_BY_PRODUCTION_DAY = _calculate_row_by_production_day()


def _calculate_first_fattening_day() -> int:
    first_fattening_day = next(
        (
            day
            for day, template_row in ROW_BY_PRODUCTION_DAY.items()
            if (
                template_row
                == default_stallkarte_production_days_mapping.fattening_start_row
            )
        ),
        None,
    )
    if first_fattening_day is None:
        raise ValueError(
            "fattening day start row is not available in production day mapping"
        )
    return first_fattening_day


# Hardcoding fattening day would duplicate knowledge and can drift if the
# template rows or skipped rows change.
THROUGHPUT_REPORT_FIRST_FATTENING_DAY = _calculate_first_fattening_day()


def get_mapping_of_production_day(
    production_day: int,
) -> StallkarteProductionDayMapping:
    """
    Returns the mapping of columns for the given production day (starting from 0).
    The mapping is the same for all production days, but the row number changes.
    """
    if production_day not in ROW_BY_PRODUCTION_DAY:
        raise ValueError(
            f"Invalid production day: {production_day}. "
            f"Valid production days are from 0 to {len(ROW_BY_PRODUCTION_DAY) - 1}."
        )

    row_number = ROW_BY_PRODUCTION_DAY[production_day]
    mp = default_stallkarte_production_days_mapping

    return StallkarteProductionDayMapping(
        day=f"{mp.day}{row_number}",
        natural_mortality=f"{mp.natural_mortality}{row_number}",
        selective_mortality=f"{mp.selective_mortality}{row_number}",
        weight=f"{mp.weight}{row_number}",
        did_inspection_1=f"{mp.did_inspection_1}{row_number}",
        did_inspection_2=f"{mp.did_inspection_2}{row_number}",
        temperature=f"{mp.temperature}{row_number}",
        humidity=f"{mp.humidity}{row_number}",
        water_consumption=f"{mp.water_consumption}{row_number}",
        feed_consumption=f"{mp.feed_consumption}{row_number}",
        annotation=f"{mp.annotation}{row_number}",
    )


def get_throughput_report_mortality_row_pairs() -> tuple[
    list[tuple[int, int]], list[tuple[int, int]]
]:
    mp = default_throughput_report_mortality_mapping

    summary_rows = range(
        mp.first_day_row,
        mp.first_day_row + THROUGHPUT_REPORT_FIRST_FATTENING_DAY,
    )

    rearing_pairs = list(
        zip(
            summary_rows,
            (
                ROW_BY_PRODUCTION_DAY[day]
                for day in range(THROUGHPUT_REPORT_FIRST_FATTENING_DAY)
            ),
            strict=True,
        )
    )
    fattening_pairs = list(
        zip(
            summary_rows,
            (
                ROW_BY_PRODUCTION_DAY[day]
                for day in range(
                    THROUGHPUT_REPORT_FIRST_FATTENING_DAY,
                    len(ROW_BY_PRODUCTION_DAY),
                )
            ),
            strict=True,
        )
    )

    return rearing_pairs, fattening_pairs
