from fastapi.testclient import TestClient

from app import domain
from app.services.database import AgriculturalHoldingCandidate
from app.services.database.repositories import AgriculturalHoldingRepository


class TestFindMyAgriculturalHolding:
    def test_find_my_holding_success(
        self,
        client: TestClient,
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

        resp = client.get("/api/v1/find-my-agricultural-holding")
        assert resp.status_code == 200
        body = resp.json()
        assert body["holding"]["name"] == "Sunny Farms"
        assert body["holding"]["owner_user_id"] == "testuser"
