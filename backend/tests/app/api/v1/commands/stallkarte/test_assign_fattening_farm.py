import pytest
from fastapi import HTTPException

from app import domain
from app.api.v1.commands.stallkarte.assign_fattening_farm import RequestBody, handler
from app.domain import AgriculturalHolding
from app.services.database import Database, FarmCandidate, FarmTypeCandidate
from app.services.database.repositories import (
    FarmRepository,
    StallkarteRepository,
)


class TestAssignFatteningFarm:
    @staticmethod
    def test_assign_fattening_farm(
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
                type=FarmTypeCandidate.FATTENING,
                vvvo_number="FF-001",
            ),
        )

        request_body = RequestBody(
            stallkarte_id=stallkarte.id,
            farm_id=farm.id,
        )

        response = handler(request_body, user, database)

        assert response.message == f"Fattening farm '{farm.id}' assigned successfully"

        updated_stallkarte = stallkarte_repository.get_stallkarte_by_id(stallkarte.id)

        assert updated_stallkarte is not None
        assert updated_stallkarte.state.fattening_farm is not None
        assert updated_stallkarte.state.fattening_farm.id == farm.id

    @staticmethod
    def test_fails_if_farm_is_not_fattening(
        database: Database,
        stallkarte_repository: StallkarteRepository,
        farm_repository: FarmRepository,
        holding: AgriculturalHolding,
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
                type=FarmTypeCandidate.REARING,
                vvvo_number="RF-001",
            ),
        )

        request_body = RequestBody(
            stallkarte_id=stallkarte.id,
            farm_id=farm.id,
        )

        with pytest.raises(domain.Exception) as exc_info:
            handler(request_body, user, database)

        e = exc_info.value
        assert str(e) == "assigned farm is not a fattening or combined farm"

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
