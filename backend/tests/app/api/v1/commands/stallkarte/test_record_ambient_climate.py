import pytest
from fastapi import HTTPException

from app import domain
from app.api.v1.commands.stallkarte.record_ambient_climate import RequestBody, handler
from app.domain import AgriculturalHolding
from app.services.database import Database
from app.services.database.repositories import (
    StallkarteRepository,
)


class TestRecordAmbientClimate:
    @staticmethod
    def test_record_ambient_climate(
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

        request_body = RequestBody(
            stallkarte_id=stallkarte.id,
            production_day=1,
            temperature_celsius=23.5,
            humidity_percent=60.0,
        )

        response = handler(request_body, user, database)

        assert (
            response.message
            == "Ambient climate recorded successfully on production day '1'"
        )

        updated_stallkarte = stallkarte_repository.get_stallkarte_by_id(stallkarte.id)

        assert updated_stallkarte is not None
        assert len(updated_stallkarte.state.days) == 1
        day = updated_stallkarte.state.days[1]
        assert day.temperature_celsius == 23.5
        assert day.humidity_percent == 60.0

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
            production_day=1,
            temperature_celsius=23.5,
            humidity_percent=60.0,
        )

        with pytest.raises(HTTPException) as exc_info:
            handler(request_body, user, database)

        e = exc_info.value
        assert e.status_code == 403
