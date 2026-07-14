import datetime

import pytest
from fastapi import HTTPException

from app import domain
from app.api.v1.commands.stallkarte.clean_silo import (
    RequestBody,
    handler,
)
from app.domain import StallkarteCycle
from app.services.database import Database
from app.services.database.repositories import StallkarteRepository


class TestCleanSilo:
    @staticmethod
    def test_clean_silo(
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
            detergent="Standard Detergent",
            dosis="2 liters per 1000 square meters",
        )

        response = handler(request_body, user, database)

        assert (
            response.message
            == "Silo cleaning completed successfully for cycle 'fattening'"
        )

        updated_stallkarte = stallkarte_repository.get_stallkarte_by_id(stallkarte.id)

        assert updated_stallkarte is not None
        assert updated_stallkarte.state.fattening_checklist is not None
        checklist = updated_stallkarte.state.fattening_checklist
        assert checklist.silo_cleaned.date == today
        assert checklist.silo_cleaned.detergent == "Standard Detergent"
        assert checklist.silo_cleaned.dosis == "2 liters per 1000 square meters"

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
            detergent="Standard Detergent",
            dosis="2 liters per 1000 square meters",
        )

        with pytest.raises(HTTPException) as exc_info:
            handler(request_body, user, database)

        e = exc_info.value
        assert e.status_code == 403
