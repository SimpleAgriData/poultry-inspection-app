from app.domain.stallkarte.event import EventPayload
from app.domain.stallkarte.events.models import NoteEntry


class GeneralNotesReplaced(
    EventPayload, event_type="stallkarte.general_notes_replaced"
):
    production_day: int
    general_notes: list[NoteEntry]
