import pytest
from fastapi import HTTPException

from app import domain
from app.api.v1.commands.stallkarte.apply_pest_control_measures import (
    RequestBody,
    handler,
)
from app.domain import StallkarteCycle
from app.services.database import Database
from app.services.database.repositories import StallkarteRepository


class TestPerformLightProgram:
    @staticmethod
    def test_apply_pest_control_measures(
        database: Database,
        stallkarte_repository: StallkarteRepository,
        holding: domain.AgriculturalHolding,
        user: domain.User,
    ) -> None:
        stallkarte = stallkarte_repository.create_stallkarte(holding.id)

        request_body = RequestBody(
            stallkarte_id=stallkarte.id,
            cycle=StallkarteCycle.FATTENING,
            did_perform_pest_control=True,
            annotation="Applied pest control measures as per guidelines.",
        )

        response = handler(request_body, user, database)

        assert response.message == "Pest control measures applied for cycle 'fattening'"

        updated_stallkarte = stallkarte_repository.get_stallkarte_by_id(stallkarte.id)

        assert updated_stallkarte is not None
        assert updated_stallkarte.state.fattening_checklist is not None
        checklist = updated_stallkarte.state.fattening_checklist
        assert checklist.pest_control_measures.did_perform_pest_control is True
        assert (
            checklist.pest_control_measures.annotation
            == "Applied pest control measures as per guidelines."
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

        request_body = RequestBody(
            stallkarte_id=other_stallkarte.id,
            cycle=StallkarteCycle.FATTENING,
            did_perform_pest_control=True,
            annotation="Applied pest control measures as per guidelines.",
        )

        with pytest.raises(HTTPException) as exc_info:
            handler(request_body, user, database)

        e = exc_info.value
        assert e.status_code == 403
