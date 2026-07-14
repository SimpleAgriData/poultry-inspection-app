from app.domain.stallkarte.event import EventPayload


class FeedConsumptionRecorded(
    EventPayload, event_type="stallkarte.feed_consumption_recorded"
):
    production_day: int
    amount_kg: float
