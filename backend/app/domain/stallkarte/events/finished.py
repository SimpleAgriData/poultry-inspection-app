import datetime

from pydantic import Field

from app.domain.stallkarte.event import EventPayload
from app.domain.stallkarte.events.models import NoteEntry


class Finished(EventPayload, event_type="stallkarte.finished"):
    date: datetime.date
    finish_notes: list[NoteEntry] = Field(default_factory=list)
