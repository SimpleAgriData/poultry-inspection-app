from app.domain.stallkarte.event.event import EventPayload


class AmbientClimateRecorded(
    EventPayload, event_type="stallkarte.ambient_climate_recorded"
):
    production_day: int
    temperature_celsius: float | None
    humidity_percent: float | None
