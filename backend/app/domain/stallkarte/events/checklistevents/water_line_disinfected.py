import datetime

from app.domain.stallkarte.event import EventPayload
from app.domain.stallkarte.events import models


class WaterLineDisinfected(
    EventPayload, event_type="stallkarte.water_line_disinfected"
):
    cycle: models.ChecklistCycle
    date: datetime.date | None
    disinfectant: str | None
    dosis: str | None
