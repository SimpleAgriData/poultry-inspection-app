from pydantic import Field

from app.domain.stallkarte.event import EventPayload
from app.domain.stallkarte.events.models import NoteEntry


class FinishNotesReplaced(EventPayload, event_type="stallkarte.finish_notes_replaced"):
    finish_notes: list[NoteEntry] = Field(default_factory=list)
