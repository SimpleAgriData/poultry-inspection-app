from app.domain.stallkarte.event import Event, EventPayload
from app.domain.stallkarte.events import (
    AlarmTestPerformed,
    AmbientClimateRecorded,
    DetailsRevised,
    FatteningDayDataRecorded,
    FatteningFarmAssigned,
    FeedConsumptionRecorded,
    FinishNotesReplaced,
    Finished,
    FlockTransferred,
    GeneralNotesReplaced,
    InstallationDetailsReplaced,
    LightingProgramPerformed,
    MortalityRecorded,
    PestControlMeasuresApplied,
    RearingFarmAssigned,
    Reopened,
    SectionNoteLogged,
    SiloCleaned,
    StableDisinfected,
    StallkarteStarted,
    TransferDetailsRevised,
    WaterConsumptionRecorded,
    WaterLineDisinfected,
    WeightRecorded,
)

events: list[type[EventPayload]] = [
    AmbientClimateRecorded,
    FatteningFarmAssigned,
    FatteningDayDataRecorded,
    FlockTransferred,
    FeedConsumptionRecorded,
    FinishNotesReplaced,
    Finished,
    StallkarteStarted,
    GeneralNotesReplaced,
    InstallationDetailsReplaced,
    MortalityRecorded,
    RearingFarmAssigned,
    SectionNoteLogged,
    WaterConsumptionRecorded,
    WeightRecorded,
    DetailsRevised,
    TransferDetailsRevised,
    AlarmTestPerformed,
    LightingProgramPerformed,
    PestControlMeasuresApplied,
    SiloCleaned,
    StableDisinfected,
    WaterLineDisinfected,
    Reopened,
]

event_lookup_table = {e.type(): e for e in events}


def parse_event(event_type: str, event_data: str) -> Event:
    event_class = event_lookup_table.get(event_type)
    if event_class is None:
        raise ValueError(f"unknown event type {event_type}")
    payload = event_class.model_validate_json(event_data)
    return Event(type=event_type, data=payload)
