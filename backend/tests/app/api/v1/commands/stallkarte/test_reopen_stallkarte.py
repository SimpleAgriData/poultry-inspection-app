import datetime

import pytest
from fastapi import HTTPException

from app import domain
from app.api.v1.commands.stallkarte.reopen_stallkarte import RequestBody, handler
from app.domain.stallkarte import events
from app.services.database import AgriculturalHoldingCandidate, Database
from app.services.database.repositories import (
    AgriculturalHoldingRepository,
    StallkarteRepository,
)


class TestReopenStallkarte:
    @staticmethod
    def test_reopen_stallkarte(
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
        holding = agricultural_holding_repository.get_holding_by_owner(user.id)

        assert holding is not None

        stallkarte = stallkarte_repository.create_stallkarte(holding.id)
        stallkarte_repository.add_event(
            stallkarte.id,
            events.Finished(date=datetime.date.today()).event(),
        )
        stallkarte_repository.mark_finished(stallkarte.id)

        response = handler(RequestBody(stallkarte_id=stallkarte.id), user, database)

        assert response.message == "Stallkarte reopened successfully"

        updated_stallkarte = stallkarte_repository.get_stallkarte_by_id(stallkarte.id)
        assert updated_stallkarte is not None
        assert updated_stallkarte.state.is_finished is False
        assert updated_stallkarte.state.date_finished is None

    @staticmethod
    def test_raises_400_if_stallkarte_not_finished(
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
        holding = agricultural_holding_repository.get_holding_by_owner(user.id)

        assert holding is not None

        stallkarte = stallkarte_repository.create_stallkarte(holding.id)

        with pytest.raises(HTTPException) as exc_info:
            handler(RequestBody(stallkarte_id=stallkarte.id), user, database)

        e = exc_info.value
        assert e.status_code == 400
        assert e.detail == "stallkarte is not finished"
