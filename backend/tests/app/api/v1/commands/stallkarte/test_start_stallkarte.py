import datetime

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app import domain
from app.api.v1.commands.stallkarte.start_stallkarte import RequestBody, handler
from app.domain import StallkarteState
from app.services.database import AgriculturalHoldingCandidate, Database
from app.services.database.repositories import (
    AgriculturalHoldingRepository,
    StallkarteRepository,
)


class TestStartStallkarte:
    @staticmethod
    def test_start_stallkarte(
        database: Database,
        agricultural_holding_repository: AgriculturalHoldingRepository,
        stallkarte_repository: StallkarteRepository,
        user: domain.User,
    ) -> None:
        holding_candidate = AgriculturalHoldingCandidate(
            owner_user_id=user.id,
            name="Sunny Farms",
            hatchery="Sunny Hatchery",
            eco_control_number="EC123456",
            breed="Breed A",
            address_street="123 Farm Lane",
            address_zip="12345",
            address_city="Farmville",
        )
        agricultural_holding_repository.add_holding(holding_candidate)

        request_body = RequestBody(
            date_started=datetime.date.today(),
            date_hatched=datetime.date.today(),
            hatchery_name="Hatchery",
            breed="A1",
            fattening_cycle="42",
            eco_control_number="123321",
            is_eu_bio=True,
            is_naturland=False,
        )

        response = handler(request_body, user, database)

        assert response.message == "Stallkarte started successfully"

        updated_stallkarte = stallkarte_repository.get_stallkarte_by_id(
            response.stallkarte_id
        )
        assert updated_stallkarte is not None
        assert updated_stallkarte.state != StallkarteState.default()
        assert updated_stallkarte.state.date_hatched == request_body.date_hatched
        assert updated_stallkarte.state.hatchery == request_body.hatchery_name
        assert updated_stallkarte.state.breed == request_body.breed
        assert updated_stallkarte.state.fattening_cycle == request_body.fattening_cycle
        assert (
            updated_stallkarte.state.eco_control_number
            == request_body.eco_control_number
        )
        assert updated_stallkarte.state.is_eu_bio == request_body.is_eu_bio
        assert updated_stallkarte.state.is_naturland == request_body.is_naturland

    @staticmethod
    def test_request_body_validation() -> None:
        with pytest.raises(ValidationError) as exc_info:
            RequestBody(
                date_started=datetime.date.today(),
                date_hatched=datetime.date.today(),
                hatchery_name="Hatchery",
                breed="A1",
                fattening_cycle="",  # Invalid: must be > 0
                eco_control_number="123321",
                is_eu_bio=True,
                is_naturland=False,
            )

        e = exc_info.value
        assert isinstance(e, ValidationError)
        errors = e.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("fattening_cycle",)
        assert errors[0]["msg"] == "String should have at least 1 character"

    @staticmethod
    def test_raises_400_if_user_has_no_holding(
        database: Database,
        user: domain.User,
    ) -> None:
        request_body = RequestBody(
            date_started=datetime.date.today(),
            date_hatched=datetime.date.today(),
            hatchery_name="Hatchery",
            breed="A1",
            fattening_cycle="42",
            eco_control_number="123321",
            is_eu_bio=True,
            is_naturland=False,
        )

        with pytest.raises(HTTPException) as exc_info:
            handler(request_body, user, database)

        e = exc_info.value
        assert e.status_code == 400
        assert e.detail == "user has no associated agricultural holding"
