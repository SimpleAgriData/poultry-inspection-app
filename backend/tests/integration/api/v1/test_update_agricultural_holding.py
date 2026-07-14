from fastapi.testclient import TestClient

from app import domain
from app.services.database import AgriculturalHoldingCandidate
from app.services.database.repositories import AgriculturalHoldingRepository


class TestUpdateAgriculturalHolding:
    @staticmethod
    def test_update_agricultural_holding_success(
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

        update_payload = {
            "holding_id": holding.id,
            "name": "Sunny Farms Updated",
            "hatchery": "New Hatchery",
            "eco_control_number": "EC654321",
            "breed": "Breed B",
            "address_street": "456 New Lane",
            "address_zip": "54321",
            "address_city": "Newville",
        }
        r2 = client.post("/api/v1/update-agricultural-holding", json=update_payload)
        assert r2.status_code == 200
        assert (
            r2.json()["message"]
            == "Agricultural Holding 'Sunny Farms Updated' updated successfully"
        )
