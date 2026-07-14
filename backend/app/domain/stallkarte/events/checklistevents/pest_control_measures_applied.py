from app.domain.stallkarte.event import EventPayload
from app.domain.stallkarte.events import models


class PestControlMeasuresApplied(
    EventPayload, event_type="stallkarte.pest_control_measures_applied"
):
    cycle: models.ChecklistCycle
    did_perform_pest_control: bool | None
    annotation: str | None
