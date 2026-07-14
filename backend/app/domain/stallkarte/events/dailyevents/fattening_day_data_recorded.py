from app.domain.stallkarte.event import EventPayload
from app.domain.stallkarte.events.models import WeatherCondition


class FatteningDayDataRecorded(
    EventPayload, event_type="stallkarte.fattening_day_data_recorded"
):
    production_day: int
    opening_time: str | None
    weather_conditions: list[WeatherCondition]
    veterinarian: bool
