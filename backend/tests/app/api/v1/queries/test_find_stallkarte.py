import pytest
from fastapi import HTTPException

from app import domain
from app.api.v1.queries.find_stallkarte import handler
from app.services.database import AgriculturalHoldingCandidate, Database
from app.services.database.repositories import (
    AgriculturalHoldingRepository,
    StallkarteRepository,
)


class TestFindStallkarte:
    @staticmethod
    def test_retrieves_stallkarte_by_id_for_authenticated_user(
        database: Database,
        agricultural_holding_repository: AgriculturalHoldingRepository,
        stallkarte_repository: StallkarteRepository,
        user: domain.User,
    ) -> None:
        holding = agricultural_holding_repository.add_holding(
            AgriculturalHoldingCandidate(
                owner_user_id=user.id,
                name="Sunny Farms",
                hatchery="Sunny Hatchery",
                eco_control_number="EC123456",
                breed="Breed A",
                address_street="123 Farm Lane",
                address_zip="12345",
                address_city="Farmville",
            )
        )

        stallkarte = stallkarte_repository.create_stallkarte(holding.id)

        response = handler(id=stallkarte.id, user=user, db=database)

        assert response.stallkarte is not None
        assert response.stallkarte.id == stallkarte.id

    @staticmethod
    def test_returns_none_if_user_has_no_associated_holding(
        database: Database,
        user: domain.User,
    ) -> None:
        response = handler(id=123, user=user, db=database)

        assert response.stallkarte is None

    @staticmethod
    def test_returns_none_if_stallkarte_not_found(
        database: Database,
        agricultural_holding_repository: AgriculturalHoldingRepository,
        user: domain.User,
    ) -> None:
        agricultural_holding_repository.add_holding(
            AgriculturalHoldingCandidate(
                owner_user_id=user.id,
                name="Sunny Farms",
                hatchery="Sunny Hatchery",
                eco_control_number="EC123456",
                breed="Breed A",
                address_street="123 Farm Lane",
                address_zip="12345",
                address_city="Farmville",
            )
        )

        response = handler(id=99999, user=user, db=database)

        assert response.stallkarte is None

    @staticmethod
    def test_raises_403_if_stallkarte_belongs_to_another_holding(
        database: Database,
        agricultural_holding_repository: AgriculturalHoldingRepository,
        stallkarte_repository: StallkarteRepository,
    ) -> None:
        # User 1
        user1 = domain.User(
            id="user1", firstname="Test", lastname="User", username="user1"
        )
        holding1 = agricultural_holding_repository.add_holding(
            AgriculturalHoldingCandidate(
                owner_user_id=user1.id,
                name="Farm 1",
                hatchery="Hatchery 1",
                eco_control_number="EC1",
                breed="Breed A",
                address_street="Street 1",
                address_zip="11111",
                address_city="City 1",
            )
        )
        stallkarte1 = stallkarte_repository.create_stallkarte(holding1.id)

        # User 2
        user2 = domain.User(
            id="user2", firstname="Test", lastname="User", username="user2"
        )
        agricultural_holding_repository.add_holding(
            AgriculturalHoldingCandidate(
                owner_user_id=user2.id,
                name="Farm 2",
                hatchery="Hatchery 2",
                eco_control_number="EC2",
                breed="Breed B",
                address_street="Street 2",
                address_zip="22222",
                address_city="City 2",
            )
        )

        # User 2 tries to access User 1's stallkarte
        with pytest.raises(HTTPException) as exc_info:
            handler(id=stallkarte1.id, user=user2, db=database)

        e = exc_info.value
        assert e.status_code == 403
        assert e.detail == "permission denied to access this Stallkarte"
