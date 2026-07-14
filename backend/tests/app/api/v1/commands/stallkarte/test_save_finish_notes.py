import pytest
from fastapi import HTTPException

from app import domain
from app.api.v1.commands.stallkarte.save_finish_notes import (
    RequestBody,
    RequestBodyFinishNoteEntry,
    handler,
)
from app.domain import AgriculturalHolding
from app.services.database import Database
from app.services.database.repositories import StallkarteRepository


class TestSaveFinishNotes:
    @staticmethod
    def test_save_finish_notes(
        database: Database,
        stallkarte_repository: StallkarteRepository,
        holding_farms_5: AgriculturalHolding,
    ) -> None:
        user = domain.User(
            firstname="Test",
            lastname="User",
            id=holding_farms_5.owner_user_id,
            username="testuser",
        )
        stallkarte = stallkarte_repository.create_stallkarte(holding_farms_5.id)

        request_body = RequestBody(
            stallkarte_id=stallkarte.id,
            finish_notes=[
                RequestBodyFinishNoteEntry(
                    id="sl-1",
                    note_type="slaughter",
                    slaughter_animals_count=1200,
                    slaughter_final_weight_kg=2.3,
                    slaughterer_name="Steinfelder",
                )
            ],
        )

        response = handler(request_body, user, database)

        assert response.message == "Finish notes saved successfully"

        updated_stallkarte = stallkarte_repository.get_stallkarte_by_id(stallkarte.id)
        assert updated_stallkarte is not None
        assert len(updated_stallkarte.state.finish_notes) == 1
        assert updated_stallkarte.state.finish_notes[0].slaughter_animals_count == 1200

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
            finish_notes=[],
        )

        with pytest.raises(HTTPException) as exc_info:
            handler(request_body, user, database)

        e = exc_info.value
        assert e.status_code == 403
