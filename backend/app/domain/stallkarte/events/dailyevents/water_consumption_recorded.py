from app.domain.stallkarte.event import EventPayload


class WaterConsumptionRecorded(
    EventPayload, event_type="stallkarte.water_consumption_recorded"
):
    production_day: int
    amount_liters: float
