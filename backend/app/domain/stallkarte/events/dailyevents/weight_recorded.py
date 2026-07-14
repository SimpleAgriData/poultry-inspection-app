from app.domain.stallkarte.event import EventPayload


class WeightRecorded(EventPayload, event_type="stallkarte.weight_recorded"):
    production_day: int
    weight_grams: float
