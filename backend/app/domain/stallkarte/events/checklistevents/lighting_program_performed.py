from app.domain.stallkarte.event import EventPayload
from app.domain.stallkarte.events import models


class LightingProgramPerformed(
    EventPayload, event_type="stallkarte.lighting_program_performed"
):
    cycle: models.ChecklistCycle
    did_dark_period_test: bool | None
    had_divergence_due_to_vet: bool | None
