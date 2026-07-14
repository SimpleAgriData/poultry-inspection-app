import datetime

import pytest
from fastapi import HTTPException

from app import domain
from app.api.v1.commands.stallkarte.assign_fattening_farm import (
    RequestBody as AssignFatteningFarmRequestBody,
)
from app.api.v1.commands.stallkarte.assign_fattening_farm import (
    handler as assign_fattening_farm_handler,
)
from app.api.v1.commands.stallkarte.transfer_flock import RequestBody, handler
from app.domain import AgriculturalHolding
from app.domain.stallkarte.stallkarte_state import StallkarteCycle
from app.services.database import Database, FarmCandidate, FarmTypeCandidate
from app.services.database.repositories import (
    FarmRepository,
    StallkarteRepository,
)


class TestStartFattening:
    @staticmethod
    def test_start_fattening(
        database: Database,
        stallkarte_repository: StallkarteRepository,
        holding_farms_5: AgriculturalHolding,
        farm_repository: FarmRepository,
    ) -> None:
        user = domain.User(
            firstname="Test",
            lastname="User",
            id=holding_farms_5.owner_user_id,
            username="testuser",
        )
        stallkarte = stallkarte_repository.create_stallkarte(holding_farms_5.id)

        farm = farm_repository.add_farm(
            holding_farms_5.id,
            FarmCandidate(
                name="Fattening Farm 1",
                type=FarmTypeCandidate.FATTENING,
                vvvo_number="FF-001",
            ),
        )

        request_body = AssignFatteningFarmRequestBody(
            stallkarte_id=stallkarte.id,
            farm_id=farm.id,
        )

        response = assign_fattening_farm_handler(request_body, user, database)

        assert response.message == f"Fattening farm '{farm.id}' assigned successfully"

        request_body = RequestBody(
            stallkarte_id=stallkarte.id,
            transfer_date=stallkarte.state.date_started,
            animals_by_section_number={1: 100},
        )

        response = handler(request_body, user, database)

        assert response.message == "Flock transferred successfully"

        updated_stallkarte = stallkarte_repository.get_stallkarte_by_id(stallkarte.id)

        assert updated_stallkarte is not None
        assert updated_stallkarte.state.current_cycle == StallkarteCycle.FATTENING
        assert updated_stallkarte.state.transfer is not None
        assert updated_stallkarte.state.transfer.date == request_body.transfer_date
        assert updated_stallkarte.state.transfer.production_day == 0
        assert updated_stallkarte.state.transfer.animals_by_section_number == {1: 100}

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

        request_body = RequestBody(
            stallkarte_id=other_stallkarte.id,
            transfer_date=datetime.date.today(),
            animals_by_section_number={1: 100},
        )

        with pytest.raises(HTTPException) as exc_info:
            handler(request_body, user, database)

        e = exc_info.value
        assert e.status_code == 403
