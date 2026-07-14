import datetime

import pytest
from fastapi import HTTPException

from app import domain
from app.api.v1.commands.stallkarte.record_fattening_day_data import (
    RequestBody,
    handler,
)
from app.domain import AgriculturalHolding
from app.domain.stallkarte import events as stallkarte_events
from app.domain.stallkarte.events.models import WeatherCondition
from app.services.database import Database
from app.services.database.repositories import StallkarteRepository


class TestRecordFatteningDayData:
    @staticmethod
    def test_record_fattening_day_data(
        database: Database,
        stallkarte_repository: StallkarteRepository,
        holding_farms_5: AgriculturalHolding,
    ) -> None:
        user = domain.User(
            firstname="Test",
            lastname="User",
            id=holding_farms_5.owner_user_id,
            username="testuser",
        )
        stallkarte = stallkarte_repository.create_stallkarte(holding_farms_5.id)

        date_started = datetime.date.today() - datetime.timedelta(days=20)
        stallkarte_repository.add_events(
            stallkarte.id,
            [
                stallkarte_events.StallkarteStarted(
                    date_started=date_started,
                    date_hatched=date_started,
                    hatchery_name="Happy Hatchery",
                    breed="Broiler",
                    fattening_cycle="Cycle-1",
                    eco_control_number="ECO-1",
                    is_eu_bio=True,
                    is_naturland=False,
                ).event(),
                stallkarte_events.FlockTransferred(
                    transfer_date=date_started + datetime.timedelta(days=10),
                    animals_by_section={1: 2000, 2: 2000},
                ).event(),
            ],
        )

        request_body = RequestBody(
            stallkarte_id=stallkarte.id,
            production_day=12,
            opening_time="08:15",
            weather_conditions=[WeatherCondition.SUN, WeatherCondition.FROST],
            veterinarian=True,
        )

        response = handler(request_body, user, database)

        assert (
            response.message
            == "Fattening day data recorded successfully on production day '12'"
        )

        updated_stallkarte = stallkarte_repository.get_stallkarte_by_id(stallkarte.id)

        assert updated_stallkarte is not None
        day = updated_stallkarte.state.days[12]
        assert day.opening_time == "08:15"
        assert day.weather_conditions == [WeatherCondition.SUN, WeatherCondition.FROST]
        assert day.veterinarian is True

    @staticmethod
    def test_raises_403_if_stallkarte_not_owned(
        database: Database,
        stallkarte_repository: StallkarteRepository,
        holding_farms_5: AgriculturalHolding,
        other_holding: domain.AgriculturalHolding,
    ) -> None:
        user = domain.User(
            firstname="Test",
            lastname="User",
            id=holding_farms_5.owner_user_id,
            username="testuser",
        )

        other_stallkarte = stallkarte_repository.create_stallkarte(other_holding.id)

        request_body = RequestBody(
            stallkarte_id=other_stallkarte.id,
            production_day=12,
            opening_time="08:15",
            weather_conditions=[WeatherCondition.SUN],
            veterinarian=False,
        )

        with pytest.raises(HTTPException) as exc_info:
            handler(request_body, user, database)

        e = exc_info.value
        assert e.status_code == 403
