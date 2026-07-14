from fastapi.testclient import TestClient

from app import domain
from app.services.database import (
    AgriculturalHoldingCandidate,
    FarmCandidate,
    FarmTypeCandidate,
    SectionCandidate,
)
from app.services.database.repositories import (
    AgriculturalHoldingRepository,
    FarmRepository,
    SectionRepository,
)


class TestDeleteSection:
    @staticmethod
    def test_delete_section_success(
        client: TestClient,
        agricultural_holding_repository: AgriculturalHoldingRepository,
        farm_repository: FarmRepository,
        section_repository: SectionRepository,
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
        section = section_repository.add_section(
            farm.id,
            SectionCandidate(name="Section 1"),
        )

        r = client.post(
            "/api/v1/delete-section",
            json={"section_id": section.id},
        )
        assert r.status_code == 200
        assert r.json()["message"] == "Section 'Section 1' deleted successfully"
