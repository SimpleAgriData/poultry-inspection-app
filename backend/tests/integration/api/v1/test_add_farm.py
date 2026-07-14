from fastapi.testclient import TestClient

from app import domain
from app.services.database import AgriculturalHoldingCandidate
from app.services.database.repositories import AgriculturalHoldingRepository


class TestAddFarm:
    @staticmethod
    def test_add_farm_success(
        client: TestClient,
        agricultural_holding_repository: AgriculturalHoldingRepository,
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

        farm_payload = {
            "agricultural_holding_id": holding.id,
            "name": "Main Farm",
            "type": "fattening",
            "vvvo_number": "VV789012",
        }
        r2 = client.post("/api/v1/add-farm", json=farm_payload)
        assert r2.status_code == 200
        data = r2.json()
        assert data["message"] == "Farm 'Main Farm' added successfully"
