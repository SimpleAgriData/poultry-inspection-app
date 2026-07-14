from enum import StrEnum

from app.domain.stallkarte.event import EventPayload


class MortalityRecordedShift(StrEnum):
    MORNING = "morning"
    EVENING = "evening"


class MortalityRecorded(EventPayload, event_type="stallkarte.mortality_recorded"):
    section_number: int
    production_day: int
    shift: MortalityRecordedShift
    natural_deaths: int | None
    selective_deaths: int | None
