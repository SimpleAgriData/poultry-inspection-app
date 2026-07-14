from fastapi.testclient import TestClient

from app import domain
from app.services.database import (
    AgriculturalHoldingCandidate,
    FarmCandidate,
    FarmTypeCandidate,
)
from app.services.database.repositories import (
    AgriculturalHoldingRepository,
    FarmRepository,
)


class TestDeleteFarm:
    @staticmethod
    def test_delete_farm_success(
        client: TestClient,
        agricultural_holding_repository: AgriculturalHoldingRepository,
        farm_repository: FarmRepository,
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
        farm = farm_repository.add_farm(
            holding.id,
            FarmCandidate(
                name="Main Farm",
                type=FarmTypeCandidate.FATTENING,
                vvvo_number="VV789012",
            ),
        )

        r = client.post("/api/v1/delete-farm", json={"farm_id": farm.id})
        assert r.status_code == 200
        assert r.json()["message"] == "Farm 'Main Farm' deleted successfully"
