# We'll treat the stallkarte state as the aggregate for now, to keep things simple.
# In the future it may be worth splitting it up further and creating a separate
# reading model.

import datetime
from enum import StrEnum, auto

from pydantic import BaseModel

from app.domain import FarmType
from app.domain.stallkarte.events.models import (
    NoteEntry,
    SectionInstallationDetails,
    WeatherCondition,
)

type SectionNumber = int


class StallkarteSection(BaseModel):
    id: int
    number: SectionNumber
    name: str


class StallkarteCycle(StrEnum):
    REARING = auto()
    FATTENING = auto()


class StallkarteFarm(BaseModel):
    id: int
    name: str
    type: FarmType
    vvvo_number: str
    sections: list[StallkarteSection]


class StallkarteStateDaySection(BaseModel):
    section_number: int
    natural_mortality_morning: int | None
    natural_mortality_evening: int | None
    selective_mortality_morning: int | None
    selective_mortality_evening: int | None
    did_inspection_morning: bool
    did_inspection_evening: bool
    note: str | None

    @classmethod
    def default(cls, section_number: int) -> "StallkarteStateDaySection":
        return cls(
            section_number=section_number,
            natural_mortality_morning=None,
            natural_mortality_evening=None,
            selective_mortality_morning=None,
            selective_mortality_evening=None,
            did_inspection_morning=False,
            did_inspection_evening=False,
            note=None,
        )


class StallkarteStateDay(BaseModel):
    production_day: int
    production_cycle: StallkarteCycle
    temperature_celsius: float | None
    humidity_percent: float | None
    weight_grams: float | None
    feed_consumption_kg: float | None
    water_consumption_liters: float | None
    opening_time: str | None
    weather_conditions: list[WeatherCondition]
    veterinarian: bool
    sections: dict[int, StallkarteStateDaySection]
    notes: list[NoteEntry]

    @classmethod
    def default(
        cls, production_day: int, production_cycle: StallkarteCycle
    ) -> "StallkarteStateDay":
        return cls(
            production_day=production_day,
            production_cycle=production_cycle,
            temperature_celsius=None,
            humidity_percent=None,
            weight_grams=None,
            feed_consumption_kg=None,
            water_consumption_liters=None,
            opening_time=None,
            weather_conditions=[],
            veterinarian=False,
            sections={},
            notes=[],
        )


class StallkarteTransfer(BaseModel):
    date: datetime.date
    production_day: int
    animals_by_section_number: dict[SectionNumber, int]


class StallkarteAlarmTest(BaseModel):
    did_emergency_power_test: bool | None
    did_alarm_test: bool | None

    @classmethod
    def default(cls) -> "StallkarteAlarmTest":
        return cls(
            did_emergency_power_test=None,
            did_alarm_test=None,
        )


class StallkarteLightingProgram(BaseModel):
    did_dark_period_test: bool | None
    had_divergence_due_to_vet: bool | None

    @classmethod
    def default(cls) -> "StallkarteLightingProgram":
        return cls(
            did_dark_period_test=None,
            had_divergence_due_to_vet=None,
        )


class StallkartePestControlMeasures(BaseModel):
    did_perform_pest_control: bool | None
    annotation: str | None

    @classmethod
    def default(cls) -> "StallkartePestControlMeasures":
        return cls(
            did_perform_pest_control=None,
            annotation=None,
        )


class StallkarteSiloCleaned(BaseModel):
    date: datetime.date | None
    detergent: str | None
    dosis: str | None

    @classmethod
    def default(cls) -> "StallkarteSiloCleaned":
        return cls(
            date=None,
            detergent=None,
            dosis=None,
        )


class StallkarteStableDisinfected(BaseModel):
    date: datetime.date | None
    disinfectant: str | None
    dosis: str | None

    @classmethod
    def default(cls) -> "StallkarteStableDisinfected":
        return cls(
            date=None,
            disinfectant=None,
            dosis=None,
        )


class StallkarteWaterLineDisinfected(BaseModel):
    date: datetime.date | None
    disinfectant: str | None
    dosis: str | None

    @classmethod
    def default(cls) -> "StallkarteWaterLineDisinfected":
        return cls(
            date=None,
            disinfectant=None,
            dosis=None,
        )


class StallkarteChecklist(BaseModel):
    alarm_test: StallkarteAlarmTest
    lighting_program: StallkarteLightingProgram
    pest_control_measures: StallkartePestControlMeasures
    silo_cleaned: StallkarteSiloCleaned
    stable_disinfected: StallkarteStableDisinfected
    water_line_disinfected: StallkarteWaterLineDisinfected

    @classmethod
    def default(cls) -> "StallkarteChecklist":
        return cls(
            alarm_test=StallkarteAlarmTest.default(),
            lighting_program=StallkarteLightingProgram.default(),
            pest_control_measures=StallkartePestControlMeasures.default(),
            silo_cleaned=StallkarteSiloCleaned.default(),
            stable_disinfected=StallkarteStableDisinfected.default(),
            water_line_disinfected=StallkarteWaterLineDisinfected.default(),
        )


class StallkarteState(BaseModel):
    fattening_farm: "StallkarteFarm | None"
    rearing_farm: "StallkarteFarm | None"
    fattening_cycle: str
    date_started: datetime.date
    date_hatched: datetime.date
    transfer: "StallkarteTransfer | None"
    hatchery: str
    breed: str
    eco_control_number: str
    current_cycle: StallkarteCycle
    is_finished: bool
    is_started: bool
    date_finished: datetime.date | None
    finish_notes: list[NoteEntry]

    rearing_checklist: StallkarteChecklist | None
    fattening_checklist: StallkarteChecklist | None

    is_eu_bio: bool
    is_naturland: bool

    days: dict[int, StallkarteStateDay]
    installation_details_by_section: dict[int, SectionInstallationDetails]

    @classmethod
    def default(cls) -> "StallkarteState":
        return cls(
            fattening_farm=None,
            rearing_farm=None,
            fattening_cycle="",
            date_started=datetime.date.min,
            date_hatched=datetime.date.min,
            transfer=None,
            hatchery="",
            breed="",
            eco_control_number="",
            current_cycle=StallkarteCycle.REARING,
            is_eu_bio=False,
            is_naturland=False,
            days={},
            installation_details_by_section={},
            is_finished=False,
            is_started=False,
            date_finished=None,
            finish_notes=[],
            rearing_checklist=None,
            fattening_checklist=None,
        )

    @property
    def current_cycle_farm(self) -> "StallkarteFarm | None":
        if self.current_cycle == StallkarteCycle.REARING:
            return self.rearing_farm
        elif self.current_cycle == StallkarteCycle.FATTENING:
            return self.fattening_farm
        return None
