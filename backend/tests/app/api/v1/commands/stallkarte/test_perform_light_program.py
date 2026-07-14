import pytest
from fastapi import HTTPException

from app import domain
from app.api.v1.commands.stallkarte.perform_light_program import (
    RequestBody,
    handler,
)
from app.domain import StallkarteCycle
from app.services.database import Database
from app.services.database.repositories import StallkarteRepository


class TestPerformLightProgram:
    @staticmethod
    def test_perform_light_program(
        database: Database,
        stallkarte_repository: StallkarteRepository,
        holding: domain.AgriculturalHolding,
        user: domain.User,
    ) -> None:
        stallkarte = stallkarte_repository.create_stallkarte(holding.id)

        request_body = RequestBody(
            stallkarte_id=stallkarte.id,
            cycle=StallkarteCycle.FATTENING,
            did_dark_period_test=True,
            had_divergence_due_to_vet=False,
        )

        response = handler(request_body, user, database)

        assert (
            response.message
            == "Light program performed successfully for cycle 'fattening'"
        )

        updated_stallkarte = stallkarte_repository.get_stallkarte_by_id(stallkarte.id)

        assert updated_stallkarte is not None
        assert updated_stallkarte.state.fattening_checklist is not None
        checklist = updated_stallkarte.state.fattening_checklist
        assert checklist.lighting_program.did_dark_period_test is True
        assert checklist.lighting_program.had_divergence_due_to_vet is False

    @staticmethod
    def test_raises_403_if_stallkarte_not_owned(
        database: Database,
        stallkarte_repository: StallkarteRepository,
        holding: domain.AgriculturalHolding,
        other_holding: domain.AgriculturalHolding,
        user: domain.User,
    ) -> None:
        other_stallkarte = stallkarte_repository.create_stallkarte(other_holding.id)

        request_body = RequestBody(
            stallkarte_id=other_stallkarte.id,
            cycle=StallkarteCycle.FATTENING,
            did_dark_period_test=True,
            had_divergence_due_to_vet=False,
        )

        with pytest.raises(HTTPException) as exc_info:
            handler(request_body, user, database)

        e = exc_info.value
        assert e.status_code == 403
