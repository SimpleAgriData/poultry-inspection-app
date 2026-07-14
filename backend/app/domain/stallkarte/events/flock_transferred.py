import datetime

from app.domain.stallkarte.event import EventPayload

type SectionNumber = int


class FlockTransferred(EventPayload, event_type="stallkarte.flock_transferred"):
    transfer_date: datetime.date
    animals_by_section: dict[SectionNumber, int]
