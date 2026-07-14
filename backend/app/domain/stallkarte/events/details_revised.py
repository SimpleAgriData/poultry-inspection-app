import datetime

from app.domain.stallkarte.event import EventPayload


class DetailsRevised(EventPayload, event_type="stallkarte.details_revised"):
    date_hatched: datetime.date
    hatchery_name: str
    breed: str
    fattening_cycle: str
    is_eu_bio: bool
    is_naturland: bool
