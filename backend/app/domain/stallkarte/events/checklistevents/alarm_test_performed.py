from app.domain.stallkarte.event import EventPayload
from app.domain.stallkarte.events import models


class AlarmTestPerformed(EventPayload, event_type="stallkarte.alarm_test_performed"):
    cycle: models.ChecklistCycle
    did_emergency_power_test: bool | None
    did_alarm_test: bool | None
