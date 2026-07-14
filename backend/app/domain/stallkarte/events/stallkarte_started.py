import datetime

from app.domain.stallkarte.event import EventPayload


class StallkarteStarted(EventPayload, event_type="stallkarte.stallkarte_started"):
    date_started: datetime.date
    date_hatched: datetime.date
    hatchery_name: str
    breed: str
    fattening_cycle: str
    eco_control_number: str
    is_eu_bio: bool
    is_naturland: bool
