from app import domain
from app.api.v1.queries.find_my_stallkarten import handler
from app.services.database import AgriculturalHoldingCandidate, Database
from app.services.database.repositories import (
    AgriculturalHoldingRepository,
    StallkarteRepository,
)


class TestFindMyStallkarten:
    @staticmethod
    def test_retrieves_stallkarten_for_authenticated_user(
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

        stallkarte1 = stallkarte_repository.create_stallkarte(holding.id)
        stallkarte2 = stallkarte_repository.create_stallkarte(holding.id)

        response = handler(user=user, db=database)

        assert len(response.active_stallkarten) == 2
        assert len(response.archived_stallkarten) == 0
        stallkarte_ids = [s.id for s in response.active_stallkarten]
        assert stallkarte1.id in stallkarte_ids
        assert stallkarte2.id in stallkarte_ids

    @staticmethod
    def test_returns_empty_list_if_user_has_no_associated_holding(
        database: Database,
        user: domain.User,
    ) -> None:

        response = handler(user=user, db=database)

        assert response.active_stallkarten == []
        assert response.archived_stallkarten == []

    @staticmethod
    def test_returns_empty_list_if_holding_has_no_active_stallkarten(
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

        response = handler(user=user, db=database)

        assert response.active_stallkarten == []
        assert response.archived_stallkarten == []

    @staticmethod
    def test_does_not_returns_archived_stallkarten(
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

        active_stallkarte = stallkarte_repository.create_stallkarte(holding.id)
        finished_stallkarte = stallkarte_repository.create_stallkarte(holding.id)
        stallkarte_repository.mark_finished(finished_stallkarte.id)

        response = handler(user=user, db=database)

        assert len(response.active_stallkarten) == 1
        assert len(response.archived_stallkarten) == 1
        assert response.active_stallkarten[0].id == active_stallkarte.id
        assert response.archived_stallkarten[0].id == finished_stallkarte.id
