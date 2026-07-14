import datetime

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app import domain
from app.api.v1.commands.stallkarte.revise_details import RequestBody, handler
from app.domain import StallkarteState
from app.services.database import Database
from app.services.database.repositories import (
    StallkarteRepository,
)


class TestReviseStallkarte:
    @staticmethod
    def test_revise_stallkarte(
        database: Database,
        stallkarte_repository: StallkarteRepository,
        user: domain.User,
        holding: domain.AgriculturalHolding,
    ) -> None:
        stallkarte = stallkarte_repository.create_stallkarte(holding.id)

        today = datetime.date.today()

        events = stallkarte.start_stallkarte(
            date_started=today,
            date_hatched=today,
            hatchery_name="Hatchery",
            breed="A1",
            fattening_cycle="42",
            eco_control_number="123321",
            is_eu_bio=True,
            is_naturland=False,
        )
        stallkarte_repository.add_events(stallkarte.id, events)

        request_body = RequestBody(
            stallkarte_id=stallkarte.id,
            date_hatched=today - datetime.timedelta(days=7),
            hatchery_name="Revised Hatchery",
            breed="Revised Breed",
            fattening_cycle="Revised Fattening Cycle",
            is_eu_bio=False,
            is_naturland=True,
        )

        response = handler(request_body, user, database)

        assert response.message == "Stallkarte details revised successfully"

        updated_stallkarte = stallkarte_repository.get_stallkarte_by_id(stallkarte.id)
        assert updated_stallkarte is not None
        assert updated_stallkarte.state != StallkarteState.default()
        assert updated_stallkarte.state.date_hatched == request_body.date_hatched
        assert updated_stallkarte.state.hatchery == "Revised Hatchery"
        assert updated_stallkarte.state.breed == "Revised Breed"
        assert updated_stallkarte.state.fattening_cycle == "Revised Fattening Cycle"
        assert not updated_stallkarte.state.is_eu_bio
        assert updated_stallkarte.state.is_naturland

    @staticmethod
    def test_request_body_validation() -> None:
        with pytest.raises(ValidationError) as exc_info:
            RequestBody(
                stallkarte_id=1,
                date_hatched=datetime.date.today(),
                hatchery_name="Hatchery",
                breed="A1",
                fattening_cycle="",  # Invalid: must have at least 1 character
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
            stallkarte_id=1,
            date_hatched=datetime.date.today(),
            hatchery_name="Hatchery",
            breed="A1",
            fattening_cycle="42",
            is_eu_bio=True,
            is_naturland=False,
        )

        with pytest.raises(HTTPException) as exc_info:
            handler(request_body, user, database)

        e = exc_info.value
        assert e.status_code == 400
        assert e.detail == "user has no associated agricultural holding"
