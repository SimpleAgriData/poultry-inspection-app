import pytest
from fastapi import HTTPException

from app import domain
from app.api.v1.queries.export_stallkarte import (
    handler,
)
from app.core.stallkarteexport import Exporter
from app.domain import AgriculturalHolding
from app.domain.stallkarte import events
from app.domain.stallkarte.events import models
from app.services.database import (
    AgriculturalHoldingCandidate,
    Database,
    FarmCandidate,
    FarmTypeCandidate,
)
from app.services.database.repositories import (
    AgriculturalHoldingRepository,
    FarmRepository,
    SectionRepository,
    StallkarteRepository,
)


class TestExportStallkarte:
    @staticmethod
    def test_exports_stallkarte_for_authenticated_user(
        database: Database,
        holding: AgriculturalHolding,
        farm_repository: FarmRepository,
        section_repository: SectionRepository,
        user: domain.User,
        exporter: Exporter,
    ) -> None:
        farm = farm_repository.add_farm(
            holding.id,
            FarmCandidate(
                type=FarmTypeCandidate.FATTENING,
                name="Main Farm",
                vvvo_number="VV789012",
            ),
        )

        stallkarte = database.stallkarte_repository.create_stallkarte(
            holding_id=holding.id,
        )

        database.stallkarte_repository.add_event(
            stallkarte.id,
            events.RearingFarmAssigned(
                farm_id=farm.id,
                farm_name=farm.name,
                farm_type=models.AssignedFarmType(farm.type.value),
                farm_vvvo_number=farm.vvvo_number,
                sections=[],
            ).event(),
        )

        response = handler(
            stallkarte_id=stallkarte.id, user=user, db=database, exporter=exporter
        )

        # This is fine for now, since testing the actual excel content is a little bit
        # too much
        assert response.status_code == 200

    @staticmethod
    def test_returns_404_if_stallkarte_not_found(
        database: Database,
        user: domain.User,
        exporter: Exporter,
    ) -> None:
        with pytest.raises(HTTPException) as exc_info:
            handler(stallkarte_id=999, user=user, db=database, exporter=exporter)

        assert exc_info.value.status_code == 404

    @staticmethod
    def test_returns_403_if_stallkarte_belongs_to_another_holding(
        database: Database,
        agricultural_holding_repository: AgriculturalHoldingRepository,
        stallkarte_repository: StallkarteRepository,
        holding: AgriculturalHolding,
        exporter: Exporter,
        user: domain.User,
    ) -> None:
        # Create a holding and stallkarte for another user
        other_user = domain.User(
            id="other_user", firstname="Other", lastname="User", username="other_user"
        )
        holding = agricultural_holding_repository.add_holding(
            AgriculturalHoldingCandidate(
                owner_user_id=other_user.id,
                name="Other Farm",
                hatchery="Other Hatchery",
                eco_control_number="EC654321",
                breed="Breed B",
                address_street="456 Other Lane",
                address_zip="54321",
                address_city="Otherville",
            )
        )

        stallkarte = stallkarte_repository.create_stallkarte(holding.id)

        with pytest.raises(HTTPException) as exc_info:
            handler(
                stallkarte_id=stallkarte.id, user=user, db=database, exporter=exporter
            )

        assert exc_info.value.status_code == 403
