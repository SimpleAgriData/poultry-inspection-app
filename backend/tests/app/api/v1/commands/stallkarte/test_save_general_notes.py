import pytest
from fastapi import HTTPException

from app import domain
from app.api.v1.commands.stallkarte.save_general_notes import (
    RequestBody,
    RequestBodyGeneralNoteEntry,
    handler,
)
from app.domain import AgriculturalHolding
from app.services.database import Database
from app.services.database.repositories import (
    StallkarteRepository,
)


class TestSaveGeneralNotes:
    @staticmethod
    def test_save_general_notes(
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
            production_day=1,
            general_notes=[
                RequestBodyGeneralNoteEntry(
                    id="note-1",
                    note_type="other",
                    note_text="General note",
                    delivery_receipt_number="AB-100",
                    batch_number="CH-100",
                )
            ],
        )

        response = handler(request_body, user, database)

        assert response.message == "General notes saved successfully"

        updated_stallkarte = stallkarte_repository.get_stallkarte_by_id(stallkarte.id)

        assert updated_stallkarte is not None
        assert len(updated_stallkarte.state.days) == 1
        day = updated_stallkarte.state.days[1]
        assert day.production_day == 1
        assert len(day.notes) == 1
        assert day.notes[0].note_text == "General note"
        assert day.notes[0].note_type == "other"
        assert day.notes[0].delivery_receipt_number == "AB-100"
        assert day.notes[0].batch_number == "CH-100"

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
            production_day=1,
            general_notes=[
                RequestBodyGeneralNoteEntry(
                    id="note-1",
                    note_type="other",
                    note_text="General note",
                )
            ],
        )

        with pytest.raises(HTTPException) as exc_info:
            handler(request_body, user, database)

        e = exc_info.value
        assert e.status_code == 403
