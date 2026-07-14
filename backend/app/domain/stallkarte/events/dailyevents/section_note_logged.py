from app.domain.stallkarte.event import EventPayload


class SectionNoteLogged(EventPayload, event_type="stallkarte.section_note_logged"):
    section_number: int
    production_day: int
    note: str
