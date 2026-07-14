import datetime

import pytest
from fastapi import HTTPException

from app import domain
from app.api.v1.commands.stallkarte.disinfect_water_line import (
    RequestBody,
    handler,
)
from app.domain import StallkarteCycle
from app.services.database import Database
from app.services.database.repositories import StallkarteRepository


class TestDisinfectWaterLine:
    @staticmethod
    def test_disinfect_water_line(
        database: Database,
        stallkarte_repository: StallkarteRepository,
        holding: domain.AgriculturalHolding,
        user: domain.User,
    ) -> None:
        stallkarte = stallkarte_repository.create_stallkarte(holding.id)

        today = datetime.date.today()

        request_body = RequestBody(
            stallkarte_id=stallkarte.id,
            cycle=StallkarteCycle.FATTENING,
            date=today,
            disinfectant="Standard Detergent",
            dosis="2 liters per 1000 square meters",
        )

        response = handler(request_body, user, database)

        assert (
            response.message
            == "Water line disinfection completed successfully for cycle 'fattening'"
        )

        updated_stallkarte = stallkarte_repository.get_stallkarte_by_id(stallkarte.id)

        assert updated_stallkarte is not None
        assert updated_stallkarte.state.fattening_checklist is not None
        checklist = updated_stallkarte.state.fattening_checklist
        assert checklist.water_line_disinfected.date == today
        assert checklist.water_line_disinfected.disinfectant == "Standard Detergent"
        assert (
            checklist.water_line_disinfected.dosis == "2 liters per 1000 square meters"
        )

    @staticmethod
    def test_raises_403_if_stallkarte_not_owned(
        database: Database,
        stallkarte_repository: StallkarteRepository,
        holding: domain.AgriculturalHolding,
        other_holding: domain.AgriculturalHolding,
        user: domain.User,
    ) -> None:
        other_stallkarte = stallkarte_repository.create_stallkarte(other_holding.id)

        today = datetime.date.today()

        request_body = RequestBody(
            stallkarte_id=other_stallkarte.id,
            cycle=StallkarteCycle.FATTENING,
            date=today,
            disinfectant="Standard Detergent",
            dosis="2 liters per 1000 square meters",
        )

        with pytest.raises(HTTPException) as exc_info:
            handler(request_body, user, database)

        e = exc_info.value
        assert e.status_code == 403
