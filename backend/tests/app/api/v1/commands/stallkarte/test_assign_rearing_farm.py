import pytest
from fastapi import HTTPException

from app import domain
from app.api.v1.commands.stallkarte.assign_rearing_farm import RequestBody, handler
from app.domain import AgriculturalHolding
from app.services.database import Database, FarmCandidate, FarmTypeCandidate
from app.services.database.repositories import (
    FarmRepository,
    StallkarteRepository,
)


class TestAssignRearingFarm:
    @staticmethod
    def test_assign_rearing_farm(
        database: Database,
        stallkarte_repository: StallkarteRepository,
        holding: AgriculturalHolding,
        farm_repository: FarmRepository,
    ) -> None:
        user = domain.User(
            firstname="Test",
            lastname="User",
            id=holding.owner_user_id,
            username="testuser",
        )
        stallkarte = stallkarte_repository.create_stallkarte(holding.id)

        farm = farm_repository.add_farm(
            holding.id,
            FarmCandidate(
                name="Rearing Farm 1",
                vvvo_number="RF12345",
                type=FarmTypeCandidate.REARING,
            ),
        )

        request_body = RequestBody(
            stallkarte_id=stallkarte.id,
            farm_id=farm.id,
        )

        response = handler(request_body, user, database)

        assert response.message == f"Rearing farm '{farm.id}' assigned successfully"

        updated_stallkarte = stallkarte_repository.get_stallkarte_by_id(stallkarte.id)

        assert updated_stallkarte is not None
        assert updated_stallkarte.state.rearing_farm is not None
        assert updated_stallkarte.state.rearing_farm.id == farm.id

    @staticmethod
    def test_fails_if_assigned_farm_is_not_rearing(
        database: Database,
        stallkarte_repository: StallkarteRepository,
        holding: AgriculturalHolding,
        farm_repository: FarmRepository,
    ) -> None:
        user = domain.User(
            firstname="Test",
            lastname="User",
            id=holding.owner_user_id,
            username="testuser",
        )
        stallkarte = stallkarte_repository.create_stallkarte(holding.id)

        farm = farm_repository.add_farm(
            holding.id,
            FarmCandidate(
                name="Fattening Farm 1",
                vvvo_number="FF12345",
                type=FarmTypeCandidate.FATTENING,
            ),
        )

        request_body = RequestBody(
            stallkarte_id=stallkarte.id,
            farm_id=farm.id,
        )

        with pytest.raises(domain.Exception) as exc_info:
            handler(request_body, user, database)

        e = exc_info.value
        assert str(e) == "assigned farm is not a rearing or combined farm"

    @staticmethod
    def test_raises_403_if_stallkarte_not_owned(
        database: Database,
        stallkarte_repository: StallkarteRepository,
        holding_farms_5: AgriculturalHolding,
        other_holding: domain.AgriculturalHolding,
    ) -> None:
        user = domain.User(
            firstname="Test",
            lastname="User",
            id=holding_farms_5.owner_user_id,
            username="testuser",
        )

        other_stallkarte = stallkarte_repository.create_stallkarte(other_holding.id)

        farm = holding_farms_5.farms[0]

        request_body = RequestBody(
            stallkarte_id=other_stallkarte.id,
            farm_id=farm.id,
        )

        with pytest.raises(HTTPException) as exc_info:
            handler(request_body, user, database)

        e = exc_info.value
        assert e.status_code == 403
