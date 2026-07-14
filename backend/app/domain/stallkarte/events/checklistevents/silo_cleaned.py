import datetime

from app.domain.stallkarte.event import EventPayload
from app.domain.stallkarte.events import models


class SiloCleaned(EventPayload, event_type="stallkarte.silo_cleaned"):
    cycle: models.ChecklistCycle
    date: datetime.date | None
    detergent: str | None
    dosis: str | None
