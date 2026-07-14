import datetime

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app import domain
from app.api.v1.commands.stallkarte.delete_stallkarte import RequestBody, handler
from app.domain.stallkarte import events
from app.services.database import AgriculturalHoldingCandidate, Database
from app.services.database.repositories import (
    AgriculturalHoldingRepository,
    StallkarteRepository,
)


class TestDeleteStallkarte:
    @staticmethod
    def test_deletes_finished_stallkarte(
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

        assert response.message == "Stallkarte deleted successfully"
        assert stallkarte_repository.get_stallkarte_by_id(stallkarte.id) is None

    @staticmethod
    def test_request_body_validation() -> None:
        with pytest.raises(ValidationError) as exc_info:
            RequestBody(stallkarte_id=0)

        e = exc_info.value
        errors = e.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("stallkarte_id",)
        assert errors[0]["msg"] == "Input should be greater than 0"

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
        assert e.detail == "only finished stallkarten can be deleted"

    @staticmethod
    def test_raises_404_if_stallkarte_not_found(
        database: Database,
        agricultural_holding_repository: AgriculturalHoldingRepository,
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

        with pytest.raises(HTTPException) as exc_info:
            handler(RequestBody(stallkarte_id=99999), user, database)

        e = exc_info.value
        assert e.status_code == 404
        assert e.detail == "stallkarte ID '99999' not found"

    @staticmethod
    def test_raises_403_if_stallkarte_belongs_to_another_holding(
        database: Database,
        agricultural_holding_repository: AgriculturalHoldingRepository,
        stallkarte_repository: StallkarteRepository,
    ) -> None:
        user1 = domain.User(
            id="user1", firstname="Test", lastname="User", username="user1"
        )
        holding_candidate1 = AgriculturalHoldingCandidate(
            owner_user_id=user1.id,
            name="Farm 1",
            hatchery="Hatchery 1",
            eco_control_number="EC1",
            breed="Breed A",
            address_street="Street 1",
            address_zip="11111",
            address_city="City 1",
        )
        agricultural_holding_repository.add_holding(holding_candidate1)
        holding1 = agricultural_holding_repository.get_holding_by_owner(user1.id)

        assert holding1 is not None

        stallkarte = stallkarte_repository.create_stallkarte(holding1.id)
        stallkarte_repository.add_event(
            stallkarte.id,
            events.Finished(date=datetime.date.today()).event(),
        )
        stallkarte_repository.mark_finished(stallkarte.id)

        user2 = domain.User(
            id="user2", firstname="Test", lastname="User", username="user2"
        )
        holding_candidate2 = AgriculturalHoldingCandidate(
            owner_user_id=user2.id,
            name="Farm 2",
            hatchery="Hatchery 2",
            eco_control_number="EC2",
            breed="Breed B",
            address_street="Street 2",
            address_zip="22222",
            address_city="City 2",
        )
        agricultural_holding_repository.add_holding(holding_candidate2)

        with pytest.raises(HTTPException) as exc_info:
            handler(RequestBody(stallkarte_id=stallkarte.id), user2, database)

        e = exc_info.value
        assert e.status_code == 403
        assert (
            e.detail
            == f"stallkarte ID '{stallkarte.id}' does not belong to the user's holding"
        )
