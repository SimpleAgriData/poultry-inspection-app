import datetime
from enum import StrEnum
from typing import Callable

from pydantic import BaseModel

from app import domain
from app.domain.stallkarte import StallkarteFarm, StallkarteSection
from app.domain.stallkarte.events.models import (
    NoteEntry,
    NoteType,
    ParentFlockEntry,
    SectionInstallationDetails,
    SockTestResult,
    TreatmentAmountUnit,
    TreatmentCode,
    VaccinationCode,
    WeatherCondition,
    WaitingTimeUnit,
)


def if_not_none[T, K](original: T | None, from_fn: Callable[[T], K]) -> K | None:
    if original is None:
        return None
    else:
        return from_fn(original)


class ResponseBodyStallkarteCycle(StrEnum):
    REARING = "rearing"
    FATTENING = "fattening"

    @staticmethod
    def from_domain(cycle: domain.StallkarteCycle) -> "ResponseBodyStallkarteCycle":
        if cycle == domain.StallkarteCycle.REARING:
            return ResponseBodyStallkarteCycle.REARING
        elif cycle == domain.StallkarteCycle.FATTENING:
            return ResponseBodyStallkarteCycle.FATTENING
        else:
            raise ValueError(f"unknown StallkarteCycle: {cycle}")


class ResponseBodyStallkarteStateSection(BaseModel):
    section_number: int
    natural_mortality_morning: int | None
    natural_mortality_evening: int | None
    selective_mortality_morning: int | None
    selective_mortality_evening: int | None
    did_inspection_morning: bool
    did_inspection_evening: bool
    note: str | None

    @staticmethod
    def from_domain(
        section: domain.StallkarteStateDaySection,
    ) -> "ResponseBodyStallkarteStateSection":
        return ResponseBodyStallkarteStateSection(
            section_number=section.section_number,
            natural_mortality_morning=section.natural_mortality_morning,
            natural_mortality_evening=section.natural_mortality_evening,
            selective_mortality_morning=section.selective_mortality_morning,
            selective_mortality_evening=section.selective_mortality_evening,
            did_inspection_morning=section.did_inspection_morning,
            did_inspection_evening=section.did_inspection_evening,
            note=section.note,
        )


class ResponseBodyGeneralNoteEntry(BaseModel):
    id: str
    note_type: NoteType
    note_text: str | None
    delivery_receipt_number: str | None
    batch_number: str | None
    vaccination_code: VaccinationCode | None
    treatment_code: TreatmentCode | None
    treatment_amount_value: float | None
    treatment_amount_unit: TreatmentAmountUnit | None
    treatment_waiting_time_value: int | None
    treatment_waiting_time_unit: WaitingTimeUnit | None
    sock_test_result: SockTestResult | None
    slaughter_date: datetime.date | None
    slaughter_animals_count: int | None
    slaughter_final_weight_kg: float | None
    slaughterer_name: str | None
    catching_time: str | None
    catcher_name: str | None

    @staticmethod
    def from_domain(note: NoteEntry) -> "ResponseBodyGeneralNoteEntry":
        return ResponseBodyGeneralNoteEntry(
            id=note.id,
            note_type=note.note_type,
            note_text=note.note_text,
            delivery_receipt_number=note.delivery_receipt_number,
            batch_number=note.batch_number,
            vaccination_code=note.vaccination_code,
            treatment_code=note.treatment_code,
            treatment_amount_value=note.treatment_amount_value,
            treatment_amount_unit=note.treatment_amount_unit,
            treatment_waiting_time_value=note.treatment_waiting_time_value,
            treatment_waiting_time_unit=note.treatment_waiting_time_unit,
            sock_test_result=note.sock_test_result,
            slaughter_date=note.slaughter_date,
            slaughter_animals_count=note.slaughter_animals_count,
            slaughter_final_weight_kg=note.slaughter_final_weight_kg,
            slaughterer_name=note.slaughterer_name,
            catching_time=note.catching_time,
            catcher_name=note.catcher_name,
        )


class ResponseBodyStallkarteDay(BaseModel):
    production_day: int
    production_cycle: ResponseBodyStallkarteCycle
    temperature_celsius: float | None
    humidity_percent: float | None
    weight_grams: float | None
    feed_consumption_kg: float | None
    water_consumption_liters: float | None
    opening_time: str | None
    weather_conditions: list[WeatherCondition]
    veterinarian: bool
    notes: list[ResponseBodyGeneralNoteEntry]
    sections: dict[int, ResponseBodyStallkarteStateSection]

    @staticmethod
    def from_domain(day: domain.StallkarteStateDay) -> "ResponseBodyStallkarteDay":
        return ResponseBodyStallkarteDay(
            production_day=day.production_day,
            production_cycle=ResponseBodyStallkarteCycle.from_domain(
                day.production_cycle
            ),
            temperature_celsius=day.temperature_celsius,
            humidity_percent=day.humidity_percent,
            weight_grams=day.weight_grams,
            feed_consumption_kg=day.feed_consumption_kg,
            water_consumption_liters=day.water_consumption_liters,
            opening_time=day.opening_time,
            weather_conditions=day.weather_conditions,
            veterinarian=day.veterinarian,
            notes=[
                ResponseBodyGeneralNoteEntry.from_domain(note) for note in day.notes
            ],
            sections={
                section_id: ResponseBodyStallkarteStateSection.from_domain(section)
                for section_id, section in day.sections.items()
            },
        )


class ResponseParentFlockEntry(BaseModel):
    herd_identifier: str
    production_week: int

    @staticmethod
    def from_domain(entry: ParentFlockEntry) -> "ResponseParentFlockEntry":
        return ResponseParentFlockEntry(
            herd_identifier=entry.herd_identifier,
            production_week=entry.production_week,
        )


class ResponseSectionInstallationDetails(BaseModel):
    section_number: int
    initial_animals_count: int
    initial_weight_grams: float
    bedding: str
    parent_flocks: list[ResponseParentFlockEntry]

    @staticmethod
    def from_domain(
        details: SectionInstallationDetails,
    ) -> "ResponseSectionInstallationDetails":
        return ResponseSectionInstallationDetails(
            section_number=details.section_number,
            initial_animals_count=details.initial_animals_count,
            initial_weight_grams=details.initial_weight_grams,
            bedding=details.bedding,
            parent_flocks=[
                ResponseParentFlockEntry.from_domain(parent_flock)
                for parent_flock in details.parent_flocks
            ],
        )


class ResponseBodySection(BaseModel):
    id: int
    number: int
    name: str

    @staticmethod
    def from_stallkarte(section: StallkarteSection) -> "ResponseBodySection":
        return ResponseBodySection(
            id=section.id,
            number=section.number,
            name=section.name,
        )


class ResponseBodyFarm(BaseModel):
    id: int
    name: str
    type: domain.FarmType
    vvvo_number: str
    sections: list[ResponseBodySection]

    @staticmethod
    def from_stallkarte(farm: StallkarteFarm) -> "ResponseBodyFarm":
        return ResponseBodyFarm(
            id=farm.id,
            name=farm.name,
            type=farm.type,
            vvvo_number=farm.vvvo_number,
            sections=[
                ResponseBodySection.from_stallkarte(section)
                for section in farm.sections
            ],
        )


type SectionNumber = int


class ResponseStallkarteTransfer(BaseModel):
    date: datetime.date
    production_day: int
    animals_by_section_number: dict[SectionNumber, int]

    @staticmethod
    def from_domain(
        transfer: domain.StallkarteTransfer,
    ) -> "ResponseStallkarteTransfer":
        return ResponseStallkarteTransfer(
            date=transfer.date,
            production_day=transfer.production_day,
            animals_by_section_number=transfer.animals_by_section_number,
        )


class ResponseStallkarteAlarmTest(BaseModel):
    did_emergency_power_test: bool | None
    did_alarm_test: bool | None

    @classmethod
    def from_domain(
        cls, alarm_test: domain.StallkarteAlarmTest
    ) -> "ResponseStallkarteAlarmTest":
        return cls(
            did_emergency_power_test=alarm_test.did_emergency_power_test,
            did_alarm_test=alarm_test.did_alarm_test,
        )


class ResponseStallkarteLightingProgram(BaseModel):
    did_dark_period_test: bool | None
    had_divergence_due_to_vet: bool | None

    @classmethod
    def from_domain(
        cls, lighting_program: domain.StallkarteLightingProgram
    ) -> "ResponseStallkarteLightingProgram":
        return cls(
            did_dark_period_test=lighting_program.did_dark_period_test,
            had_divergence_due_to_vet=lighting_program.had_divergence_due_to_vet,
        )


class ResponseStallkartePestControlMeasures(BaseModel):
    did_perform_pest_control: bool | None
    annotation: str | None

    @classmethod
    def from_domain(
        cls, pest_control_measures: domain.StallkartePestControlMeasures
    ) -> "ResponseStallkartePestControlMeasures":
        return cls(
            did_perform_pest_control=pest_control_measures.did_perform_pest_control,
            annotation=pest_control_measures.annotation,
        )


class ResponseStallkarteSiloCleaned(BaseModel):
    date: datetime.date | None
    detergent: str | None
    dosis: str | None

    @classmethod
    def from_domain(
        cls, silo_cleaned: domain.StallkarteSiloCleaned
    ) -> "ResponseStallkarteSiloCleaned":
        return cls(
            date=silo_cleaned.date,
            detergent=silo_cleaned.detergent,
            dosis=silo_cleaned.dosis,
        )


class ResponseStallkarteStableDisinfected(BaseModel):
    date: datetime.date | None
    disinfectant: str | None
    dosis: str | None

    @classmethod
    def from_domain(
        cls, stable_disinfected: domain.StallkarteStableDisinfected
    ) -> "ResponseStallkarteStableDisinfected":
        return cls(
            date=stable_disinfected.date,
            disinfectant=stable_disinfected.disinfectant,
            dosis=stable_disinfected.dosis,
        )


class ResponseStallkarteWaterLineDisinfected(BaseModel):
    date: datetime.date | None
    disinfectant: str | None
    dosis: str | None

    @classmethod
    def from_domain(
        cls, water_line_disinfected: domain.StallkarteWaterLineDisinfected
    ) -> "ResponseStallkarteWaterLineDisinfected":
        return cls(
            date=water_line_disinfected.date,
            disinfectant=water_line_disinfected.disinfectant,
            dosis=water_line_disinfected.dosis,
        )


class ResponseStallkarteChecklist(BaseModel):
    alarm_test: ResponseStallkarteAlarmTest
    lighting_program: ResponseStallkarteLightingProgram
    pest_control_measures: ResponseStallkartePestControlMeasures
    silo_cleaned: ResponseStallkarteSiloCleaned
    stable_disinfected: ResponseStallkarteStableDisinfected
    water_line_disinfected: ResponseStallkarteWaterLineDisinfected

    @classmethod
    def from_domain(
        cls, checklist: domain.StallkarteChecklist
    ) -> "ResponseStallkarteChecklist":
        return cls(
            alarm_test=ResponseStallkarteAlarmTest.from_domain(checklist.alarm_test),
            lighting_program=ResponseStallkarteLightingProgram.from_domain(
                checklist.lighting_program
            ),
            pest_control_measures=ResponseStallkartePestControlMeasures.from_domain(
                checklist.pest_control_measures
            ),
            silo_cleaned=ResponseStallkarteSiloCleaned.from_domain(
                checklist.silo_cleaned
            ),
            stable_disinfected=ResponseStallkarteStableDisinfected.from_domain(
                checklist.stable_disinfected
            ),
            water_line_disinfected=ResponseStallkarteWaterLineDisinfected.from_domain(
                checklist.water_line_disinfected
            ),
        )


class ResponseBodyStallkarteState(BaseModel):
    breed: str
    current_cycle: ResponseBodyStallkarteCycle
    date_started: datetime.date
    date_hatched: datetime.date
    days: dict[int, ResponseBodyStallkarteDay]
    eco_control_number: str
    fattening_farm: ResponseBodyFarm | None
    rearing_farm: ResponseBodyFarm | None
    fattening_cycle: str
    is_finished: bool
    date_finished: datetime.date | None
    hatchery: str
    is_eu_bio: bool
    is_naturland: bool
    transfer: ResponseStallkarteTransfer | None
    finish_notes: list[ResponseBodyGeneralNoteEntry]
    installation_details_by_section: dict[int, ResponseSectionInstallationDetails]

    rearing_checklist: ResponseStallkarteChecklist | None
    fattening_checklist: ResponseStallkarteChecklist | None

    @staticmethod
    def from_domain(state: domain.StallkarteState) -> "ResponseBodyStallkarteState":
        return ResponseBodyStallkarteState(
            breed=state.breed,
            current_cycle=ResponseBodyStallkarteCycle.from_domain(state.current_cycle),
            fattening_cycle=state.fattening_cycle,
            date_started=state.date_started,
            date_hatched=state.date_hatched,
            days={
                production_day: ResponseBodyStallkarteDay.from_domain(day)
                for production_day, day in state.days.items()
            },
            eco_control_number=state.eco_control_number,
            fattening_farm=if_not_none(
                state.fattening_farm, ResponseBodyFarm.from_stallkarte
            ),
            is_finished=state.is_finished,
            date_finished=state.date_finished,
            hatchery=state.hatchery,
            is_eu_bio=state.is_eu_bio,
            is_naturland=state.is_naturland,
            rearing_farm=if_not_none(
                state.rearing_farm, ResponseBodyFarm.from_stallkarte
            ),
            transfer=if_not_none(
                state.transfer, ResponseStallkarteTransfer.from_domain
            ),
            finish_notes=[
                ResponseBodyGeneralNoteEntry.from_domain(note)
                for note in state.finish_notes
            ],
            installation_details_by_section={
                section_number: ResponseSectionInstallationDetails.from_domain(details)
                for section_number, details in (
                    state.installation_details_by_section.items()
                )
            },
            rearing_checklist=if_not_none(
                state.rearing_checklist,
                ResponseStallkarteChecklist.from_domain,
            ),
            fattening_checklist=if_not_none(
                state.fattening_checklist,
                ResponseStallkarteChecklist.from_domain,
            ),
        )


class ResponseBodyStallkarte(BaseModel):
    id: int
    holding_id: int
    state: ResponseBodyStallkarteState

    @staticmethod
    def from_domain(stallkarte: domain.Stallkarte) -> "ResponseBodyStallkarte":
        return ResponseBodyStallkarte(
            id=stallkarte.id,
            holding_id=stallkarte.holding_id,
            state=ResponseBodyStallkarteState.from_domain(stallkarte.state),
        )
