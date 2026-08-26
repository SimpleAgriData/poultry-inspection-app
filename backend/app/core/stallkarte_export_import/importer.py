from __future__ import annotations

import datetime
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, BinaryIO, Type, cast
from pathlib import Path
from collections import defaultdict
import re
import uuid
from collections.abc import Callable
from typing import TypeVar
import openpyxl
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from app import domain
from app.core.stallkarte_export_import.mapping import (
    YesNoMapping,
    default_export_worksheet_names,
    default_throughput_report_header_mapping as mp_throughput_header,
    default_throughput_report_finish_notes_mapping as mp_throughput_finish_notes,
    default_stallkarte_holding_mapping as mp_holding,
    default_stallkarte_production_days_mapping as mp_production_days,
    default_stallkarte_checklist_mapping as mp_checklist,
    default_outdoor_journal_days_mapping as mp_outdoor_journal_days,
    default_throughput_report_general_notes_mapping as mp_throughput_general_notes,
)
from app.core.stallkarte_export_import.note_parser import (
    parse_general_notes,
    extract_treatment_amount_and_text,
)
from app.domain.stallkarte.stallkarte import Stallkarte
from app.domain.stallkarte.apply import StallkarteAggregator
from app.services.database import Database
from app.domain.farm import FarmType

from app.domain.stallkarte.events import models
from app.domain.stallkarte.events.dailyevents.mortality_recorded import (
    MortalityRecordedShift,
)
from app.services.database.repositories.section import SectionCandidate
from app.domain.stallkarte.stallkarte_state import StallkarteCycle
from app.core.stallkarte_export_import.errors import StallkarteImportError


class Importer:
    def __init__(self, source: str | Path | BinaryIO) -> None:
        self.workbook: Workbook = openpyxl.load_workbook(
            source,
            data_only=True,
        )

        self.daily_event_rows: list[int] = []
        self.excepetion_only_one_farm: bool = False
        self.throughput_report: Worksheet
        self.first_section_ws: Worksheet
        self.outdoor_journal: Worksheet
        self.section_sheet_names: list[str]
    
    Number = TypeVar("Number", int, float)

    def import_stallkarte(
        self,
        holding: domain.AgriculturalHolding,
        db: Database,
    ) -> Stallkarte:
        """
        Sets up the <b>stallkarte</b>  and reads data from the workbook to create domain events, which are persisted to the database and applied to the stallkarte aggregate. Returns the fully constructed stallkarte.
        """

        self._validate_workbook_structure()

        self.section_sheet_names = self._get_section_sheet_names()
        self.first_section_ws = self._worksheet(self.section_sheet_names[0])
        self.throughput_report = self._worksheet(
            default_export_worksheet_names.throughput_report_name
        )
        self.outdoor_journal = self._worksheet(
            default_export_worksheet_names.outdoor_journal_name
        )
        date_started: datetime.date = self._read_required_date(
            self.first_section_ws,
            mp_production_days.date + str(mp_production_days.start_row),
            "date_started",
        )
        self.daily_event_rows = self._build_daily_event_rows(date_started)

        start_payload = self._read_start_payload(self.throughput_report, date_started)

        stallkarte = db.stallkarte_repository.create_stallkarte(
            holding.id, commit=False
        )

        start_events = stallkarte.start_stallkarte(
            date_started=start_payload.date_started,
            date_hatched=start_payload.date_hatched,
            hatchery_name=start_payload.hatchery_name,
            breed=start_payload.breed,
            fattening_cycle=start_payload.fattening_cycle,
            eco_control_number=start_payload.eco_control_number,
            is_eu_bio=start_payload.is_eu_bio,
            is_naturland=start_payload.is_naturland,
        )
        self._persist_events(db, stallkarte, start_events)
        StallkarteAggregator.apply_to(stallkarte, holding.farms, start_events)

        farm_assignment_events = self._read_farm_assignment_events(
            holding, db, stallkarte
        )
        self._persist_events(db, stallkarte, farm_assignment_events)
        StallkarteAggregator.apply_to(stallkarte, holding.farms, farm_assignment_events)

        installation_detail_events = self._read_installation_detail_events(stallkarte)
        self._persist_events(db, stallkarte, installation_detail_events)
        StallkarteAggregator.apply_to(
            stallkarte, holding.farms, installation_detail_events
        )

        transfer_events = self._read_transfer_events(stallkarte)
        self._persist_events(db, stallkarte, transfer_events)
        StallkarteAggregator.apply_to(stallkarte, holding.farms, transfer_events)

        checklist_events = self._read_checklist_events(stallkarte)
        self._persist_events(db, stallkarte, checklist_events)
        StallkarteAggregator.apply_to(stallkarte, holding.farms, checklist_events)

        daily_events = self._read_daily_events(stallkarte)
        self._persist_events(db, stallkarte, daily_events)
        StallkarteAggregator.apply_to(stallkarte, holding.farms, daily_events)

        finish_events = self._read_finish_events(stallkarte)
        self._persist_events(db, stallkarte, finish_events)
        db.stallkarte_repository.mark_finished(stallkarte.id, commit=False)
        StallkarteAggregator.apply_to(stallkarte, holding.farms, finish_events)

        return stallkarte

    def _persist_events(
        self,
        db: Database,
        stallkarte: Stallkarte,
        events: list[domain.StallkarteEvent],
    ) -> None:
        for event in events:
            db.stallkarte_repository.add_event(stallkarte.id, event, commit=False)

    def _validate_workbook_structure(self) -> None:
        required_sheet_names = [
            default_export_worksheet_names.quality_report_bio_chicks_name,
            default_export_worksheet_names.throughput_report_name,
            default_export_worksheet_names.outdoor_journal_name,
        ]

        missing_sheet_names = [
            sheet_name
            for sheet_name in required_sheet_names
            if sheet_name not in self.workbook.sheetnames
        ]

        if missing_sheet_names:
            raise StallkarteImportError(
                code="missing_sheets",
                message="Invalid workbook structure. Missing required sheets.",
                german_display_message="Der Importer konnte die folgenden Arbeitsblätter nicht finden: "
                + ", ".join(missing_sheet_names),
            )

    def _get_section_sheet_names(self) -> list[str]:
        prefix = default_export_worksheet_names.section_title_prefix
        section_sheet_names = [
            name
            for name in self.workbook.sheetnames
            if name.startswith(prefix) or name.startswith("Abteil")
        ]
        return section_sheet_names

    def _worksheet(self, sheet_name: str) -> Worksheet:
        if sheet_name not in self.workbook.sheetnames:
            raise StallkarteImportError(
                code="sheet_not_found",
                message=f"worksheet '{sheet_name}' not found",
                german_display_message=f"Arbeitsblatt '{sheet_name}' konnte nicht gefunden werden.",
            )
        return self.workbook[sheet_name]

    def _parse_section_number(self, title: str) -> str:
        value = title.split(" ", 1)[1]
        if title.startswith("Abteil "):
            return value.rsplit(".", 1)[-1]
        return value

    @dataclass(slots=True)
    class _StartPayload:
        date_started: datetime.date
        date_hatched: datetime.date
        hatchery_name: str
        breed: str
        fattening_cycle: str
        eco_control_number: str
        is_eu_bio: bool
        is_naturland: bool

    def _read_start_payload(
        self,
        ws: Worksheet,
        date_started: datetime.date,
    ) -> "Importer._StartPayload":

        def as_bool(value: object) -> bool:
            return str(value).strip().upper() in {"X", "TRUE", "1", "JA"}

        return Importer._StartPayload(
            date_started=date_started,
            date_hatched=self._read_required_date(
                ws,
                mp_throughput_header.date_hatched_cell,
                "date_hatched",
            ),
            hatchery_name=ws[mp_throughput_header.hatchery_cell].value,
            breed=ws[mp_throughput_header.breed_cell].value,
            fattening_cycle=ws[mp_throughput_header.fattening_cycle_cell].value,
            eco_control_number=ws[mp_throughput_header.eco_control_number_cell].value,
            is_eu_bio=as_bool(ws[mp_throughput_header.eu_bio_cell].value),
            is_naturland=as_bool(ws[mp_throughput_header.naturland_cell].value),
        )

    def _read_farm_assignment_events(
        self,
        holding: domain.AgriculturalHolding,
        db: Database,
        stallkarte: domain.Stallkarte,
    ) -> list[domain.StallkarteEvent]:

        def resolve_farm(vvvo_number: str | int, farm_type: FarmType) -> domain.Farm:
            normalized_vvvo_number = str(vvvo_number).strip()
            farm_id = db.farm_repository.get_farm_id_by_vvonr(normalized_vvvo_number)
            farm = next((item for item in holding.farms if item.id == farm_id), None)
            if farm is None:
                raise StallkarteImportError(
                    code="farm_not_found",
                    message=f"{farm_type} farm with VVO number '{normalized_vvvo_number}' not found in holding",
                    german_display_message=f"{farm_type} Farm mit VVO-Nummer '{normalized_vvvo_number}' konnte für den Betrieb nicht gefunden werden.",
                )
            if farm.type != farm_type:
                farms_in_holding = db.farm_repository.get_farms_by_holding_id(
                    holding.id
                )
                for farm_in_holding in farms_in_holding:
                    if farm_in_holding.type == farm_type:
                        farm_id = farm_in_holding.id
                        farm = next(
                            (item for item in holding.farms if item.id == farm_id), None
                        )

            for section in self._get_section_sheet_names():
                section_number = int(self._parse_section_number(section))
                add_section_to_farm(section_number, farm)

            return farm

        def add_section_to_farm(section_number: int, farm: domain.Farm) -> None:
            if not hasattr(farm, "sections") or farm.sections is None:
                farm.sections = []

            for existing in farm.sections:
                try:
                    if str(getattr(existing, "name", "")) == str(section_number):
                        return
                except Exception:
                    continue

            try:
                created = db.section_repository.add_section(
                    farm.id, SectionCandidate(name=str(section_number))
                )
                if created is not None:
                    farm.sections.append(created)
                    return
            except Exception:
                pass

            # Fallback: create a domain.Section in-memory and attach it to the farm
            try:
                sec = domain.Section(
                    id=section_number, name=str(section_number), farm=farm
                )
                farm.sections.append(sec)
            except Exception:
                # ignore any issues creating the in-memory object
                pass

        rearing_vvonr = self.throughput_report[
            mp_throughput_header.rearing_vvvo_number_cell
        ].value
        fattening_vvonr = self.throughput_report[
            mp_throughput_header.fattening_vvvo_number_cell
        ].value

        if rearing_vvonr == fattening_vvonr:
            self.excepetion_only_one_farm = True

        events = stallkarte.assign_rearing_farm(
            resolve_farm(rearing_vvonr, FarmType.REARING)
        )
        if fattening_vvonr:
            events.extend(
                stallkarte.assign_fattening_farm(
                    resolve_farm(fattening_vvonr, FarmType.FATTENING)
                )
            )

        return events

    def _read_installation_detail_events(
        self,
        stallkarte: domain.Stallkarte,
    ) -> list[domain.StallkarteEvent]:

        section_details: list[models.SectionInstallationDetails] = []
        section_one_ws = self._worksheet(self.section_sheet_names[0])

        def split_multi_value_cell(value: object) -> list[str]:
            if value is None:
                return []

            normalized_value = str(value).replace(";", ",")
            return [
                part.strip() for part in normalized_value.split(",") if part.strip()
            ]

        for section in self.section_sheet_names:
            ws = self._worksheet(section)

            parent_flocks_from_cell = []
            for parent_flock in split_multi_value_cell(
                ws[mp_holding.parent_flock].value
            ):
                parent_flock = re.sub(
                    r"(?i)^\s*stall(?=\s|\d|-|_|$)[\s_-]*", "", parent_flock
                )
                if parent_flock:
                    parent_flocks_from_cell.append(parent_flock)

            production_weeks_from_cell = split_multi_value_cell(
                ws[mp_holding.production_week].value
            )

            if (
                len(production_weeks_from_cell) == 1
                and len(parent_flocks_from_cell) > 1
            ):
                production_weeks_from_cell = production_weeks_from_cell * len(
                    parent_flocks_from_cell
                )

            # Allowed: either exactly one parent flock and one production week,
            # or the same number of parent flocks and production weeks.
            if not (
                (
                    len(parent_flocks_from_cell) == 1
                    and len(production_weeks_from_cell) == 1
                )
                or (len(parent_flocks_from_cell) == len(production_weeks_from_cell))
            ):  # TODO: noch sinnvoll?
                raise StallkarteImportError(
                    code="invalid_parent_flock_production_week",
                    message=f"Invalid parent flock / production week configuration in section {ws.title}: "
                    + f"parent_flocks={len(parent_flocks_from_cell)}, production_weeks={len(production_weeks_from_cell)}",
                    german_display_message=f"Ungültige Konmbintaion von Elterntieren / Produktionswochen in {ws.title}: "
                    + f"Anzahl der Elterntierherden={len(parent_flocks_from_cell)}, Anzahl der Produktionswochen={len(production_weeks_from_cell)}",
                )
            first_day_weight_recorded_cell_address: str = (
                self._find_first_day_weight_recorded_cell_address(section_one_ws)
            )

            initial_animals_count = self._read_optional_int(ws, mp_holding.animals_count, "initial_animals_count")
            if initial_animals_count is None:
                raise StallkarteImportError(
                    code="missing_initial_animals_count",
                    message=f"Missing initial animals count in section {ws.title}",
                    german_display_message=f"Fehlende Tieranzahl in Zelle {mp_holding.animals_count} in {ws.title}",
                )

            bedding = self.throughput_report[mp_throughput_header.bedding_cell].value
            if bedding is None:
                raise StallkarteImportError(
                    code="missing_bedding",
                    message=f"Missing bedding information in section {ws.title}",
                    german_display_message=f"Fehlende Einstreuinformationen in Zelle {mp_throughput_header.bedding_cell} im Durchgangsbericht",
                )
            current_section = models.SectionInstallationDetails(
                section_number=self._parse_section_number(ws.title),
                initial_animals_count=initial_animals_count,
                # initial weight grams assumed to be first weight entry
                initial_weight_grams=self._read_required_int(
                    section_one_ws,
                    first_day_weight_recorded_cell_address,
                    "initial_weight_grams"
                ),
                bedding=bedding,
                parent_flocks=[
                    models.ParentFlockEntry(
                        herd_identifier=entry,
                        production_week=production_weeks_from_cell[idx],
                    )
                    for idx, entry in enumerate(parent_flocks_from_cell)
                ],
            )
            section_details.append(current_section)

        events = stallkarte.replace_installation_details(
            section_details=section_details
        )
        return events

    def _read_transfer_events(
        self,
        stallkarte: domain.Stallkarte,
    ) -> list[domain.StallkarteEvent]:
        first_section_ws = self._worksheet(self.section_sheet_names[0])

        transfer_date = self._parse_optional_date_cell(
            self.throughput_report,
            mp_throughput_header.transfer_date_cell,
            "transfer_date",
        )
        if transfer_date is None:
            transfer_date = self._search_transfer_date()

        animals_by_section_number: dict[int, int] = {}
        transfer_row = None

        for row in self.daily_event_rows:
            if (
                self._read_required_date(
                    first_section_ws, mp_production_days.date + str(row), "date"
                )
                == transfer_date
            ):
                transfer_row = row
                break
        if transfer_row is None:
            raise StallkarteImportError(
                code="transfer_row_not_found",
                message=f"Transfer row for date {transfer_date} not found in daily event rows.",
                german_display_message=f"Die Zeile für die Umstallung am {transfer_date} konnte nicht gefunden werden.",
            )

        for section in self.section_sheet_names:
            ws = self._worksheet(section)
            init_animals_count = self._read_required_int(
                ws, mp_holding.animals_count, "animals_count"
            )

            animals_on_transfer_date = init_animals_count - self._read_required_int(
                ws, mp_production_days.cumulative_mortality + str(transfer_row), "cumulative_mortality"
            )

            animals_by_section_number[int(self._parse_section_number(ws.title))] = (
                animals_on_transfer_date
            )

        events = stallkarte.transfer_flock(
            transfer_date=transfer_date,
            animals_by_section_number=animals_by_section_number,
        )
        return events

    def _read_checklist_events(
        self, stallkarte: domain.Stallkarte
    ) -> list[domain.StallkarteEvent]:

        # assuming checklist values are supposed to be identical across sections
        # default to REARING as this is an extension not provided by throughput report excel sheets
        cycle = StallkarteCycle.REARING

        events = stallkarte.apply_pest_control_measures(
            cycle=cycle,
            did_perform_pest_control=self._read_yes_no(
                self.first_section_ws, mp_checklist.did_pest_control_measures
            ),
            annotation=self.first_section_ws[
                mp_checklist.pest_control_measures_annotation
            ].value,
        )

        silo_detergent_dosis = self._parse_optional_percent_cell(
            self.first_section_ws,
            mp_checklist.silo_detergent_dosis,
            return_float=False,
        )
        if silo_detergent_dosis is not None:
            silo_detergent_dosis = str(silo_detergent_dosis)
       
        # default to first of the year for entry jährlich
        silo_cleaning_date_value = self.first_section_ws[
            mp_checklist.silo_cleaning_date
        ].value
        if (
            isinstance(silo_cleaning_date_value, str)
            and silo_cleaning_date_value.strip().lower() == "jährlich"
        ):
            clean_silo_year = self._read_required_date(
                self.first_section_ws,
                mp_holding.date_hatched,
                "date_hatched",
            )
            clean_silo_date = datetime.date(clean_silo_year.year, 1, 1)
        elif silo_cleaning_date_value is None or silo_cleaning_date_value == "":
            clean_silo_date = None
        else:
            clean_silo_date = self._parse_date_value(
                silo_cleaning_date_value,
                cell_ref=mp_checklist.silo_cleaning_date,
                field_name="silo_cleaning_date",
                allow_empty=False,
            )

        events.extend(
            stallkarte.clean_silo(
                cycle=cycle,
                date=clean_silo_date,
                detergent=self.first_section_ws[mp_checklist.silo_detergent].value,
                dosis=silo_detergent_dosis,
            )
        )
        stable_disinfectant_dosis_cell_ref = mp_checklist.stable_disinfectant_dosis
        stable_disinfectant_dosis = self._parse_optional_percent_cell(
            self.first_section_ws,
            stable_disinfectant_dosis_cell_ref,
            return_float=False,
        )
        if stable_disinfectant_dosis is not None:
            stable_disinfectant_dosis = str(stable_disinfectant_dosis)
        

        stable_disinfection_date = self._parse_optional_date_cell(
            self.first_section_ws,
            mp_checklist.stable_disinfection_date,
            "stable_disinfection_date",
        )

        events.extend(
            stallkarte.disinfect_stable(
                cycle=cycle,
                date=stable_disinfection_date,
                disinfectant=self.first_section_ws[
                    mp_checklist.stable_disinfectant
                ].value,
                dosis=stable_disinfectant_dosis,
            )
        )
        water_line_disinfectant_dosis= self._parse_optional_percent_cell(
            self.first_section_ws,
            mp_checklist.water_line_disinfectant_dosis,
            return_float=False,
        )
        if water_line_disinfectant_dosis is not None:
            water_line_disinfectant_dosis = str(water_line_disinfectant_dosis)
       

        water_line_disinfection_date = self._parse_optional_date_cell(
            self.first_section_ws,
            mp_checklist.water_line_disinfection_date,
            "water_line_disinfection_date",
        )

        events.extend(
            stallkarte.disinfect_water_line(
                cycle=cycle,
                date=water_line_disinfection_date,
                disinfectant=self.first_section_ws[
                    mp_checklist.water_line_disinfectant
                ].value,
                dosis=water_line_disinfectant_dosis,
            )
        )

        events.extend(
            stallkarte.perform_alarm_test(
                cycle=cycle,
                did_emergency_power_test=self._read_yes_no(
                    self.first_section_ws, mp_checklist.did_emergency_power_test
                ),
                did_alarm_test=self._read_yes_no(
                    self.first_section_ws, mp_checklist.did_alarm_test
                ),
            )
        )

        events.extend(
            stallkarte.perform_lighting_program(
                cycle=cycle,
                did_dark_period_test=self._read_yes_no(
                    self.first_section_ws, mp_checklist.did_dark_period_test
                ),
                had_divergence_due_to_vet=self._read_yes_no(
                    self.first_section_ws, mp_checklist.had_deviations_due_to_vet
                ),
            )
        )

        return events

    def _read_daily_events(
        self, stallkarte: domain.Stallkarte
    ) -> list[domain.StallkarteEvent]:

        first_section_ws = self._worksheet(self.section_sheet_names[0])
        outdoor_journal_events: list[domain.StallkarteEvent] | None = []
        section_events: list[domain.StallkarteEvent] = []
        current_outdoor_journal_row: int = mp_outdoor_journal_days.first_data_row
        throughput_report_note_entries: dict[datetime.date, list[models.NoteEntry]] = (
            self._extract_throughput_report_note_entries(self.throughput_report)
        )

        for row_number in self.daily_event_rows:
            production_day = self._read_required_int(
                first_section_ws,
                mp_production_days.day + str(row_number),
                "production_day",
            )
            
            humidity_cell_ref = mp_production_days.humidity + str(row_number)
            humidity_percent = self._parse_optional_percent_cell(
                first_section_ws,
                humidity_cell_ref,
                return_float=True
            )
            if humidity_percent is not None:
                humidity_percent = float(humidity_percent)

            temperature_cell_ref = mp_production_days.temperature + str(row_number)
            temperature_celsius = self._read_optional_float(first_section_ws, temperature_cell_ref, "temperature_celsius")

            if temperature_celsius is not None and not isinstance(temperature_celsius, (int, float)):
                raise StallkarteImportError(
                    code="invalid_temperature_format",
                    message=f"Temperature in {temperature_cell_ref} must be a number.",
                    german_display_message=f"Temperatur in Zelle: {temperature_cell_ref} muss eine Zahl oder leer sein.",
                )
            
            section_events.extend(
                stallkarte.record_ambient_climate(
                    production_day=production_day,
                    temperature_celsius=temperature_celsius,
                    humidity_percent=humidity_percent,
                )
            )

            amount_kg = self._read_optional_float(
                first_section_ws,
                mp_production_days.feed_consumption + str(row_number),
                "amount_kg",
            )
            if amount_kg is None:
                amount_kg = 0.0

            section_events.extend(
                stallkarte.record_feed_consumption(
                    production_day=production_day, amount_kg=amount_kg
                )
            )
            amount_liters = self._read_optional_float(
                first_section_ws,
                mp_production_days.water_consumption + str(row_number),
                "amount_liters",
            )
            if amount_liters is None:
                amount_liters = 0.0

            section_events.extend(
                stallkarte.record_water_consumption(
                    production_day=production_day, amount_liters=amount_liters
                )
            )
            weight_grams = self._read_optional_float(
                first_section_ws,
                mp_production_days.weight + str(row_number),
                "weight_grams",
            )
            if weight_grams is None:
                weight_grams = 0.0

            section_events.extend(
                stallkarte.record_weight(
                    production_day=production_day, weight_grams=weight_grams
                )
            )

            outdoor_journal_events = self._read_outdoor_journal_events(
                row_number=row_number,
                current_outdoor_journal_row=current_outdoor_journal_row,
                stallkarte=stallkarte,
            )

            if outdoor_journal_events is not None:
                section_events.extend(outdoor_journal_events)
                current_outdoor_journal_row += (
                    mp_outdoor_journal_days.default_data_row_count
                )

            production_date = self._read_required_date(
                first_section_ws,
                mp_production_days.date + str(row_number),
                "production_date",
            )
            throughput_report_notes: list[models.NoteEntry] | None = (
                throughput_report_note_entries.get(production_date, [])
            )
            general_notes: list[domain.StallkarteEvent] | None = self._read_notes(
                row_number=row_number,
                stallkarte=stallkarte,
                production_day=production_day,
                throughput_report_notes=throughput_report_notes,
            )
            if general_notes is not None:
                section_events.extend(general_notes)

        for section in self.section_sheet_names:
            ws = self._worksheet(section)
            section_number = self._parse_section_number(ws.title)
            for row_number in self.daily_event_rows:
                production_day = self._read_required_int(
                    ws,
                    mp_production_days.day + str(row_number),
                    "production_day",
                )

                natural_deaths: int | None = self._read_optional_int(
                    ws, mp_production_days.natural_mortality + str(row_number), "natural_deaths"
                )

                selective_deaths: int | None = self._read_optional_int(
                    ws, mp_production_days.selective_mortality + str(row_number), "selective_deaths"
                )

                section_events.extend(
                    stallkarte.record_mortality(
                        production_day=production_day,
                        section_number=int(section_number),
                        natural_deaths=natural_deaths,
                        selective_deaths=selective_deaths,
                        # defaulting to morning shift, as the exported excel sheets do not contain shift information
                        shift=MortalityRecordedShift.MORNING,
                    )
                )

        return section_events

    def _read_finish_events(
        self,
        stallkarte: domain.Stallkarte,
    ) -> list[domain.StallkarteEvent]:

        catching_notes: list[models.NoteEntry] = []
        slaughter_notes: list[models.NoteEntry] = []
        for i in range(3):
            catching_time = self.throughput_report[
                mp_throughput_finish_notes.catching_time_cells[i]
            ].value
            catcher_name = self.throughput_report[
                mp_throughput_finish_notes.catching_catcher_cells[i]
            ].value
            if (catching_time is None and catching_time == "") or (
                catcher_name is None and catcher_name == ""
            ):
                continue
            catching_notes.append(
                models.NoteEntry(
                    id=str(uuid.uuid4()),
                    note_type=models.NoteType.CATCHING,
                    catching_time=str(catching_time),
                    catcher_name=catcher_name,
                )
            )

        for i in range(3):
            slaughter_row = mp_throughput_finish_notes.slaughter_rows[i]
            slaughter_date = self.throughput_report[
                mp_throughput_finish_notes.slaughter_date_column + str(slaughter_row)
            ].value
            slaughter_animals_count = self.throughput_report[
                mp_throughput_finish_notes.slaughter_animals_count_column
                + str(slaughter_row)
            ].value
            slaughterer_name = self.throughput_report[
                mp_throughput_finish_notes.slaughter_slaughterer_column
                + str(slaughter_row)
            ].value

            last_weight_row = self.daily_event_rows[len(self.daily_event_rows) - 1]
            slaughter_final_weight_kg = self.first_section_ws[
                mp_production_days.weight + str(last_weight_row)
            ].value
            if slaughter_final_weight_kg is None or slaughter_final_weight_kg == "":
                slaughter_final_weight_kg = self.first_section_ws[
                    mp_production_days.weight + str(last_weight_row - 1)
                ].value

            if (slaughter_date is not None and slaughter_date != "") or (
                slaughter_animals_count is not None and slaughter_animals_count != ""
            ):
                continue
            slaughter_notes.append(
                models.NoteEntry(
                    id=str(uuid.uuid4()),
                    note_type=models.NoteType.SLAUGHTER,
                    slaughter_date=slaughter_date,
                    slaughter_animals_count=slaughter_animals_count,
                    slaughterer_name=slaughterer_name,
                    slaughter_final_weight_kg=slaughter_final_weight_kg,
                )
            )

        slaughter_date = self._read_required_date(
            self.throughput_report,
            mp_throughput_finish_notes.slaughter_date_column
            + str(mp_throughput_finish_notes.slaughter_rows[0]),
            "slaughter_date",
        )
        events = stallkarte.finish(
            date=slaughter_date, finish_notes=catching_notes + slaughter_notes
        )
        return events

    ##Helpers
    def _read_yes_no(self, ws: Worksheet, mapping: YesNoMapping) -> bool:
        value = ws[mapping.yes].value
        if isinstance(value, str):
            value = value.strip().lower()
        return value in {"ja", "yes"}

    def _parse_optional_date_cell(
        self,
        ws: Worksheet,
        cell_ref: str,
        field_name: str,
    ) -> datetime.date | None:
        return self._parse_date_value(
            ws[cell_ref].value,
            cell_ref=cell_ref,
            field_name=field_name,
            allow_empty=True,
        )

    def _read_required_date(
        self,
        ws: Worksheet,
        cell_ref: str,
        field_name: str,
    ) -> datetime.date:
        parsed_value = self._parse_date_value(
            ws[cell_ref].value,
            cell_ref=cell_ref,
            field_name=field_name,
            allow_empty=False,
        )
        assert parsed_value is not None
        return parsed_value

    def _build_daily_event_rows(
        self,
        date_started: datetime.date,
    ) -> list[int]:
        catching_cell = mp_throughput_finish_notes.catching_date_cells[0]
        end_date = self._read_required_date(
            self.throughput_report,
            catching_cell,
            "catching_date_1",
        )

        stallkarte_duration_days = (end_date - date_started).days
        if stallkarte_duration_days < 0:
            raise StallkarteImportError(
                code="invalid_duration",
                message=f"catching_date_1 ({end_date}) is before date_started ({date_started}).",
                german_display_message=f"Das Fangdatum ({end_date}) liegt vor dem Startdatum ({date_started}).",
            )

        actual_production_days_end_row = (
            mp_production_days.start_row
            + stallkarte_duration_days
            + len(mp_production_days.skipped_rows)
            - 1
        )

        return [
            row_number
            for row_number in range(
                mp_production_days.start_row,
                actual_production_days_end_row + 1,
            )
            if row_number not in mp_production_days.skipped_rows
        ]

    def _parse_date_value(
        self,
        value: object,
        *,
        cell_ref: str,
        field_name: str,
        allow_empty: bool,
    ) -> datetime.date | None:
        if value is None or value == "":
            if allow_empty:
                return None
            raise StallkarteImportError(
                code="invalid_date_format",
                message=f"{field_name} in {cell_ref} must contain a date.",
                german_display_message=f"Feld: {field_name} in Zelle: {cell_ref} muss ein Datum sein.",
            )

        if isinstance(value, datetime.datetime):
            return value.date()

        if isinstance(value, datetime.date):
            return value

        if isinstance(value, str):
            stripped_value = value.strip()
            if not stripped_value:
                if allow_empty:
                    return None
                raise StallkarteImportError(
                    code="invalid_date_format",
                    message=f"{field_name} in {cell_ref} must contain a date.",
                    german_display_message=f"Feld:{field_name} in Zelle: {cell_ref} muss ein Datum sein.",
                )

            for date_format in ("%d.%m.%Y", "%Y-%m-%d"):
                try:
                    return datetime.datetime.strptime(
                        stripped_value, date_format
                    ).date()
                except ValueError:
                    continue

            raise StallkarteImportError(
                code="invalid_date_format",
                message=f"{field_name} in {cell_ref} must be a date like DD.MM.YYYY, got {value!r}.",
                german_display_message=f"Feld: {field_name} in Zelle: {cell_ref} muss ein Datum in dem Format DD.MM.YYYY sein, aber es wurde {type(value).__name__}: {value!r} gefunden.",
            )
        raise StallkarteImportError(
            code="invalid_date_format",
            message=f"{field_name} in {cell_ref} must be a date, got {type(value).__name__}: {value!r}.",
            german_display_message=f"Feld: {field_name} in Zelle: {cell_ref} muss ein Datum sein, aber es wurde {type(value).__name__}: {value!r} gefunden.",
        )

    def _parse_optional_percent_cell(
        self,
        ws: Worksheet,
        cell_ref: str,
        return_float: bool,
    ) -> float | str | None:
        "Returns float or None for return_float=True and str or None for return_float=False"
        cell = ws[cell_ref]
        value = cell.value

        if value is None or value == "":
            return None

        if isinstance(value, str):
            stripped_value = value.strip()
            if not stripped_value:
                return None
            if stripped_value.endswith("%"):
                stripped_value = stripped_value[:-1].strip()
            if return_float:
                return float(stripped_value)
            return stripped_value

        numeric_value = float(value)
        number_format = str(cell.number_format or "")

        # Excel stores percentage-formatted numbers as fractions (e.g., 0.55 for 55%).
        if "%" in number_format and abs(numeric_value) <= 1:
            return round(numeric_value * 100, 10)

        if return_float:
            return numeric_value
        return str(numeric_value)

    def _find_first_day_weight_recorded_cell_address(self, ws: Worksheet) -> str:
        for row_number in self.daily_event_rows:
            weight_cell_address = mp_production_days.weight + str(row_number)
            weight_value = self._read_optional_float(ws, weight_cell_address, "weight")
            if weight_value is not None:
                return weight_cell_address
        raise StallkarteImportError(
            code="no_weight_recorded",
            message="No recorded weight found in the production days range.",
            german_display_message="Es wurde kein Gewichtseintrag in den Produktionszeilen gefunden.",
        )

    def _extract_general_notes(self, value: str | None) -> list[models.NoteEntry]:
        notes_from_annotations: list[models.NoteEntry] = parse_general_notes(value)

        return notes_from_annotations

    def _determine_weather_conditions(
        self, outdoor_journal: Worksheet, row_number: int
    ) -> list[models.WeatherCondition]:
        conditions_list: list[models.WeatherCondition] = []
        if str(
            outdoor_journal[mp_outdoor_journal_days.sun_column + str(row_number)].value
        ).strip().lower() in {"x", "xx", "ja", "yes", "1", "true"}:
            conditions_list.append(models.WeatherCondition.SUN)
        if str(
            outdoor_journal[
                mp_outdoor_journal_days.cloudy_column + str(row_number)
            ].value
        ).strip().lower() in {"x", "xx", "ja", "yes", "1", "true"}:
            conditions_list.append(models.WeatherCondition.CLOUDY)
        if str(
            outdoor_journal[
                mp_outdoor_journal_days.precipitation_column + str(row_number)
            ].value
        ).strip().lower() in {"x", "xx", "ja", "yes", "1", "true"}:
            conditions_list.append(models.WeatherCondition.PRECIPITATION)
        if str(
            outdoor_journal[
                mp_outdoor_journal_days.extreme_wetness_column + str(row_number)
            ].value
        ).strip().lower() in {"x", "xx", "ja", "yes", "1", "true"}:
            conditions_list.append(models.WeatherCondition.EXTREME_WETNESS)
        if str(
            outdoor_journal[
                mp_outdoor_journal_days.frost_column + str(row_number)
            ].value
        ).strip().lower() in {"x", "xx", "ja", "yes", "1", "true"}:
            conditions_list.append(models.WeatherCondition.FROST)
        if str(
            outdoor_journal[
                mp_outdoor_journal_days.strong_wind_column + str(row_number)
            ].value
        ).strip().lower() in {"x", "xx", "ja", "yes", "1", "true"}:
            conditions_list.append(models.WeatherCondition.STRONG_WIND)

        return conditions_list

    def _match_enum_code(
        self,
        raw_value: str | None,
        enum_cls: Type[StrEnum],
        *,
        use_word_boundary: bool = False,
    ) -> None | StrEnum:
        "Matches a raw text value against the members of a given code enum, such as vaccination codes or treatment codes, and returns the corresponding enum member if a match is found. It normalizes the input, checks for an exact match first, and then optionally falls back to word-boundary or substring matching depending on the code type."
        if raw_value is None:
            return None

        normalized = str(raw_value).lower().strip()

        for code in enum_cls:
            if normalized == code.value:
                return code

        for code in enum_cls:
            if use_word_boundary:
                if re.search(rf"\b{re.escape(code.value)}\b", normalized):
                    return code
            else:
                if code.value in normalized:
                    return code

        return None

    def _extract_throughput_report_note_entries(
        self, throughput_report: Worksheet
    ) -> dict[datetime.date, list[models.NoteEntry]]:
        note_entries_by_date = defaultdict(list)

        for row in mp_throughput_general_notes.vaccination_rows:
            delivery_receipt_number = throughput_report[
                mp_throughput_general_notes.vaccination_delivery_receipt_column
                + str(row)
            ].value
            batch_number: str | None = throughput_report[
                mp_throughput_general_notes.vaccination_batch_number_column + str(row)
            ].value
            vaccination_code_str = throughput_report[
                mp_throughput_general_notes.vaccination_code_column + str(row)
            ].value

            if (
                delivery_receipt_number is None
                and batch_number is None
                and vaccination_code_str is None
            ):
                continue

            date = self._read_required_date(
                throughput_report,
                mp_throughput_general_notes.vaccination_date_column + str(row),
                "vaccination_date",
            )

            vaccination_code = self._match_enum_code(
                vaccination_code_str, models.VaccinationCode, use_word_boundary=True
            )

            vacc_entry = models.NoteEntry(
                id=str(uuid.uuid4()),
                note_type=models.NoteType.VACCINATION,
                delivery_receipt_number=delivery_receipt_number,
                batch_number=str(batch_number),
                vaccination_code=vaccination_code,
            )
            note_entries_by_date[date].append(vacc_entry)

        for row in mp_throughput_general_notes.treatment_rows:
            delivery_receipt_number = throughput_report[
                mp_throughput_general_notes.treatment_delivery_receipt_column + str(row)
            ].value
            batch_number: str | None = throughput_report[
                mp_throughput_general_notes.treatment_batch_number_column + str(row)
            ].value
            treatment_code_str = throughput_report[
                mp_throughput_general_notes.treatment_treatment_code_column + str(row)
            ].value
            treatment_amount_str = throughput_report[
                mp_throughput_general_notes.treatment_amount_column + str(row)
            ].value
            treatment_waiting_time = self._read_optional_int(
                throughput_report,
                mp_throughput_general_notes.treatment_waiting_time_column + str(row),
                "treatment_waiting_time"
            )

            if (
                delivery_receipt_number is None
                and batch_number is None
                and treatment_code_str is None
            ):
                continue

            treatment_start_date = self._read_required_date(
                throughput_report,
                mp_throughput_general_notes.treatment_start_date_column + str(row),
                "treatment_start_date",
            )
            treatment_end_date = self._read_required_date(
                throughput_report,
                mp_throughput_general_notes.treatment_end_date_column + str(row),
                "treatment_end_date",
            )

            treatment_code = self._match_enum_code(
                treatment_code_str, models.TreatmentCode, use_word_boundary=False
            )

            treatment_amount_value = None
            treatment_amount_unit = None
            if treatment_amount_str is not None:
                treatment_amount_value, treatment_amount_unit, _ = (
                    extract_treatment_amount_and_text(str(treatment_amount_str))
                )

            treatment_entry = models.NoteEntry(
                id=str(uuid.uuid4()),
                note_type=models.NoteType.TREATMENT,
                delivery_receipt_number=delivery_receipt_number,
                batch_number=str(batch_number),
                treatment_code=treatment_code,
                treatment_amount_value=treatment_amount_value,
                treatment_amount_unit=treatment_amount_unit,
                treatment_waiting_time_unit=models.WaitingTimeUnit.DAY,  # assuming day default
                treatment_waiting_time_value=int(treatment_waiting_time)
                if treatment_waiting_time is not None
                else None,
            )

            for date in self._daterange(treatment_start_date, treatment_end_date):
                note_entries_by_date[date].append(treatment_entry.copy())

        sock_test_result = self._read_yes_no(
            throughput_report, mp_throughput_general_notes.sock_test_result
        )

        if sock_test_result is not None:
            sock_test_date = self._parse_optional_date_cell(
                throughput_report,
                mp_throughput_general_notes.sock_test_date,
                "sock_test_date",
            )
            # defaulting to a the date 10 days before slaughtering if no entry
            if sock_test_date is None:
                sock_test_date = self._read_required_date(
                    self.first_section_ws,
                    mp_production_days.date
                    + str(self.daily_event_rows[len(self.daily_event_rows) - 11]),
                    "sock_test_date",
                )

            sock_test_result_type = (
                models.SockTestResult.NEGATIVE
                if sock_test_result
                else models.SockTestResult.POSITIVE
            )

            sock_test_entry = models.NoteEntry(
                id=str(uuid.uuid4()),
                note_type=models.NoteType.SOCK_TEST,
                sock_test_result=sock_test_result_type,
            )
            note_entries_by_date[sock_test_date].append(sock_test_entry)

        return dict(note_entries_by_date)

    def _daterange(
        self, start_date: datetime.date, end_date: datetime.date
    ) -> list[datetime.date]:
        dates: list[datetime.date] = []
        for n in range((end_date - start_date).days + 1):
            dates.append(start_date + datetime.timedelta(days=n))
        return dates

    def _notes_overlap(
        self, general_note: models.NoteEntry, throughput_note: models.NoteEntry
    ) -> bool:
        if general_note.note_type != throughput_note.note_type:
            return False

        if general_note.note_type == models.NoteType.VACCINATION:
            return general_note.vaccination_code == throughput_note.vaccination_code

        if general_note.note_type == models.NoteType.TREATMENT:
            return general_note.treatment_code == throughput_note.treatment_code

        if general_note.note_type == models.NoteType.SOCK_TEST:
            return True

        return False

    def _merge_note(
        self, general_note: models.NoteEntry, throughput_note: models.NoteEntry
    ) -> models.NoteEntry:
        if throughput_note.note_type == models.NoteType.VACCINATION:
            merged_note = general_note.copy()
            merged_note.delivery_receipt_number = (
                throughput_note.delivery_receipt_number
            )
            merged_note.batch_number = throughput_note.batch_number
            return merged_note

        if throughput_note.note_type == models.NoteType.TREATMENT:
            merged_note = general_note.copy()
            merged_note.delivery_receipt_number = (
                throughput_note.delivery_receipt_number
            )
            merged_note.batch_number = throughput_note.batch_number
            merged_note.treatment_amount_value = general_note.treatment_amount_value
            merged_note.treatment_amount_unit = general_note.treatment_amount_unit
            merged_note.treatment_waiting_time_value = (
                throughput_note.treatment_waiting_time_value
            )
            merged_note.treatment_waiting_time_unit = (
                throughput_note.treatment_waiting_time_unit
            )
            return merged_note

        if throughput_note.note_type == models.NoteType.SOCK_TEST:
            return throughput_note.copy()

        return general_note.copy()

    def _merge_notes(
        self,
        general_notes: list[models.NoteEntry],
        throughput_report_notes: list[models.NoteEntry],
    ) -> list[models.NoteEntry]:
        merged_notes: list[models.NoteEntry] = []
        used_general_indices: set[int] = set()
        used_throughput_indices: set[int] = set()

        for t_idx, throughput_note in enumerate(throughput_report_notes):
            match_found = False

            for g_idx, general_note in enumerate(general_notes):
                if g_idx in used_general_indices:
                    continue

                if self._notes_overlap(general_note, throughput_note):
                    merged_notes.append(self._merge_note(general_note, throughput_note))
                    used_general_indices.add(g_idx)
                    used_throughput_indices.add(t_idx)
                    match_found = True
                    break

            if not match_found:
                merged_notes.append(throughput_note)

        for g_idx, general_note in enumerate(general_notes):
            if g_idx not in used_general_indices:
                merged_notes.append(general_note)

        return merged_notes

    def _search_transfer_date(self) -> datetime.date:
        "Searches for transfer_date in different parts of the Workbook"
        if self.excepetion_only_one_farm:
            transfer_date = self._parse_optional_date_cell(
                self.outdoor_journal,
                mp_outdoor_journal_days.date_column
                + str(mp_outdoor_journal_days.first_data_row),
                "transfer_date",
            )
            if transfer_date is not None:
                return transfer_date
            else:
                raise StallkarteImportError(
                    code="transfer_date_not_found",
                    message="Transfer date not found in outdoor journal for exception case.",
                    german_display_message="Das Umstallungsdatum konnte für den Sonderfall: 'Gleiche Mast und Aufzuchtsfarm' nicht im Außlaufjournal festgestellt werden.",
                )

        for section in self.section_sheet_names:
            ws = self._worksheet(section)
            transfer_date = self._parse_optional_date_cell(
                ws, mp_holding.date_transferred, "transfer_date"
            )
            if transfer_date is not None:
                return transfer_date

        transfer_date = self._find_transfer_date_from_annotations()
        if transfer_date is not None:
            return transfer_date
        else:
            raise StallkarteImportError(
                code="transfer_date_not_found",
                message="Transfer date not found in any section or relocation note.",
                german_display_message="Das Umstallungsdatum konnte in keinem Abteil oder durch eine Bemerkung zur Umstallung gefunden werden.",
            )

    def _find_transfer_date_from_annotations(self) -> datetime.date | None:
        first_section_ws = self._worksheet(self.section_sheet_names[0])

        for row_number in self.daily_event_rows:
            production_date = self._read_required_date(
                first_section_ws,
                mp_production_days.date + str(row_number),
                "production_date",
            )
            note_value = first_section_ws[
                mp_production_days.annotation + str(row_number)
            ].value
            if not note_value:
                continue

            notes = self._extract_general_notes(note_value)
            if any(note.note_type == models.NoteType.RELOCATION for note in notes):
                return production_date

        return None

    def _read_outdoor_journal_events(
        self,
        row_number: int,
        current_outdoor_journal_row: int,
        stallkarte: domain.Stallkarte,
    ) -> list[domain.StallkarteEvent] | None:
        first_section_ws = self._worksheet(self.section_sheet_names[0])

        start_date_outdoor_journal = self._read_required_date(
            self.outdoor_journal,
            mp_outdoor_journal_days.date_column
            + str(mp_outdoor_journal_days.first_data_row),
            "start_date_outdoor_journal",
        )
        current_production_date = self._read_required_date(
            first_section_ws,
            mp_production_days.date + str(row_number),
            "current_production_date",
        )
        if start_date_outdoor_journal is not None or start_date_outdoor_journal != "":
            if (
                current_production_date >= start_date_outdoor_journal
            ):
                production_day_outdoor_journal = self._read_required_int(
                    first_section_ws,
                    mp_production_days.day + str(row_number),
                    "production_day_outdoor_journal",
                )
                veterinarian: bool = (
                    True
                    if self.outdoor_journal[
                        mp_outdoor_journal_days.veterinarian_column
                        + str(current_outdoor_journal_row)
                    ].value
                    in ["x", "xx", "ja", "yes", "1", "true"]
                    else False
                )

                opening_time_cell_value = str(
                    self.outdoor_journal[
                        mp_outdoor_journal_days.opening_time_column
                        + str(current_outdoor_journal_row)
                    ].value
                )#TODO: correct wrong spelling : ; .

                outdoor_journal_events: list[domain.StallkarteEvent] = (
                    stallkarte.record_fattening_day_data(
                        production_day=production_day_outdoor_journal,
                        opening_time=opening_time_cell_value,
                        weather_conditions=self._determine_weather_conditions(
                            self.outdoor_journal, current_outdoor_journal_row
                        ),
                        veterinarian=veterinarian,
                    )
                )
                return outdoor_journal_events
            else:
                return None
        else:
            return None

    def _read_notes(
        self,
        row_number: int,
        stallkarte: domain.Stallkarte,
        production_day: int,
        throughput_report_notes: list[models.NoteEntry] | None,
    ) -> list[domain.StallkarteEvent] | None:
        first_section_ws = self._worksheet(self.section_sheet_names[0])

        general_note_cell_value = first_section_ws[
            mp_production_days.annotation + str(row_number)
        ].value

        if general_note_cell_value is not None and general_note_cell_value != "":
            general_notes: list[models.NoteEntry] = self._extract_general_notes(
                general_note_cell_value
            )
        else:
            general_notes: list[models.NoteEntry] = []
        merged_notes: list[models.NoteEntry] = []

        if throughput_report_notes is not None:
            merged_notes = self._merge_notes(general_notes, throughput_report_notes)
        else:
            merged_notes = general_notes

        if merged_notes and len(merged_notes) > 0:
            note_events: list[domain.StallkarteEvent] = stallkarte.save_general_notes(
                production_day=production_day,
                general_notes=merged_notes,
            )
            return note_events
        else:
            return None


    def _normalize_number_value(self, value: Any) -> Any:
        if not isinstance(value, str):
            return value

        normalized = value.strip()

        # Deutsche Schreibweise, z. B. "1.234,56" → "1234.56"
        if "," in normalized and "." in normalized:
            if normalized.rfind(",") > normalized.rfind("."):
                return normalized.replace(".", "").replace(",", ".")

            # Englische Schreibweise, z. B. "1,234.56" → "1234.56"
            return normalized.replace(",", "")

        # Deutsche Dezimalzahl, z. B. "21,5" → "21.5"
        if "," in normalized:
            return normalized.replace(",", ".")

        return normalized

    def _read_number(
        self,
        ws: Worksheet,
        cell_ref: str,
        field_name: str,
        *,
        required: bool,
        converter: Callable[[Any], Number],
        number_type_name: str,
    ) -> Number | None:
        raw_value: Any = ws[cell_ref].value
        
        if raw_value is None or raw_value == "":
            if not required:
                return None

            raise StallkarteImportError(
                code="invalid_number_format",
                message=f"{field_name} in {cell_ref} must contain an {number_type_name}.",
                german_display_message=(
                    f"Feld: {field_name} in Zelle: {cell_ref} muss eine Zahl enthalten."
                ),
            )
        
        value = self._normalize_number_value(raw_value)

        try:
            return converter(value)
        except (ValueError, TypeError) as error:
            expectation = (
                f"an {number_type_name}"
                if required
                else f"an {number_type_name} or empty"
            )

            raise StallkarteImportError(
                code="invalid_number_format",
                message=(
                    f"{field_name} in {cell_ref} must be {expectation}, "
                    f"got {type(value).__name__}: {raw_value!r}."
                ),
                german_display_message=(
                    f"Feld: {field_name} in Zelle: {cell_ref} muss eine Zahl"
                    f"{' oder leer' if not required else ''} sein, aber es wurde "
                    f"{type(value).__name__}: {raw_value!r} gefunden."
                ),
            ) from error

    def _read_required_float(
        self,
        ws: Worksheet,
        cell_ref: str,
        field_name: str,
    ) -> float:
        return cast(
            float,
            self._read_number(
                ws,
                cell_ref,
                field_name,
                required=True,
                converter=float,
                number_type_name="float",
            ),
    )


    def _read_optional_float(
        self,
        ws: Worksheet,
        cell_ref: str,
        field_name: str,
    ) -> float | None:
        return self._read_number(
            ws, cell_ref, field_name,
            required=False,
            converter=float,
            number_type_name="float",
        )


    def _read_required_int(
        self,
        ws: Worksheet,
        cell_ref: str,
        field_name: str,
    ) -> int:
        return cast(
            int,
            self._read_number(
                ws,
                cell_ref,
                field_name,
                required=True,
                converter=int,
                number_type_name="integer",
            ),
        )


    def _read_optional_int(
        self,
        ws: Worksheet,
        cell_ref: str,
        field_name: str,
    ) -> int | None:
        return self._read_number(
            ws, cell_ref, field_name,
            required=False,
            converter=int,
            number_type_name="integer",
        )
    
__all__ = ["Importer", "Stallkarte"]
