import datetime

import pytest
from fastapi import HTTPException

from app import domain
from app.api.v1.commands.stallkarte.finish_stallkarte import (
    RequestBody,
    RequestBodyFinishNoteEntry,
    handler,
)
from app.domain.stallkarte.events import models
from app.services.database import AgriculturalHoldingCandidate, Database
from app.services.database.repositories import (
    AgriculturalHoldingRepository,
    StallkarteRepository,
)


class TestFinishStallkarte:
    @staticmethod
    def test_finish_stallkarte(
        database: Database,
        agricultural_holding_repository: AgriculturalHoldingRepository,
        stallkarte_repository: StallkarteRepository,
        user: domain.User,
    ) -> None:
        holding_candidate = AgriculturalHoldingCandidate(
            owner_user_id=user.id,
            name="Sunny Farms",
            hatchery="Sunny Hatchery",
            eco_control_number="EC123456",
            breed="Breed A",
            address_street="123 Farm Lane",
            address_zip="12345",
            address_city="Farmville",
        )
        agricultural_holding_repository.add_holding(holding_candidate)
        holding = agricultural_holding_repository.get_holding_by_owner(user.id)

        assert holding is not None

        stallkarte = stallkarte_repository.create_stallkarte(holding.id)

        finish_date = datetime.date.today()
        request_body = RequestBody(
            stallkarte_id=stallkarte.id,
            date_finished=finish_date,
        )

        response = handler(request_body, user, database)

        assert response.message == "Stallkarte finished successfully"

        updated_stallkarte = stallkarte_repository.get_stallkarte_by_id(stallkarte.id)
        assert updated_stallkarte is not None
        assert updated_stallkarte.state.is_finished is True
        assert updated_stallkarte.state.date_finished == finish_date
        assert updated_stallkarte.state.finish_notes == []

    @staticmethod
    def test_finish_stallkarte_with_finish_notes(
        database: Database,
        agricultural_holding_repository: AgriculturalHoldingRepository,
        stallkarte_repository: StallkarteRepository,
        user: domain.User,
    ) -> None:
        holding_candidate = AgriculturalHoldingCandidate(
            owner_user_id=user.id,
            name="Sunny Farms",
            hatchery="Sunny Hatchery",
            eco_control_number="EC123456",
            breed="Breed A",
            address_street="123 Farm Lane",
            address_zip="12345",
            address_city="Farmville",
        )
        agricultural_holding_repository.add_holding(holding_candidate)
        holding = agricultural_holding_repository.get_holding_by_owner(user.id)

        assert holding is not None

        stallkarte = stallkarte_repository.create_stallkarte(holding.id)

        finish_date = datetime.date.today()
        request_body = RequestBody(
            stallkarte_id=stallkarte.id,
            date_finished=finish_date,
            finish_notes=[
                RequestBodyFinishNoteEntry(
                    id="sl-1",
                    note_type="slaughter",
                    slaughter_date=finish_date,
                    slaughter_animals_count=1234,
                    slaughter_final_weight_kg=2.4,
                    slaughterer_name="Steinfelder",
                ),
                RequestBodyFinishNoteEntry(
                    id="ca-1",
                    note_type="catching",
                    catching_time="05:45",
                    catcher_name="Team Nord",
                ),
            ],
        )

        response = handler(request_body, user, database)

        assert response.message == "Stallkarte finished successfully"

        updated_stallkarte = stallkarte_repository.get_stallkarte_by_id(stallkarte.id)
        assert updated_stallkarte is not None
        assert len(updated_stallkarte.state.finish_notes) == 2
        assert (
            updated_stallkarte.state.finish_notes[0].note_type
            == models.NoteType.SLAUGHTER
        )
        assert updated_stallkarte.state.finish_notes[0].slaughter_animals_count == 1234

    @staticmethod
    def test_raises_400_if_user_has_no_holding(
        database: Database,
        user: domain.User,
    ) -> None:
        finish_date = datetime.date.today()

        request_body = RequestBody(
            stallkarte_id=123,
            date_finished=finish_date,
        )

        with pytest.raises(HTTPException) as exc_info:
            handler(request_body, user, database)

        e = exc_info.value
        assert e.status_code == 400
        assert e.detail == "user has no associated agricultural holding"

    @staticmethod
    def test_raises_404_if_stallkarte_not_found(
        database: Database,
        agricultural_holding_repository: AgriculturalHoldingRepository,
        user: domain.User,
    ) -> None:
        holding_candidate = AgriculturalHoldingCandidate(
            owner_user_id=user.id,
            name="Sunny Farms",
            hatchery="Sunny Hatchery",
            eco_control_number="EC123456",
            breed="Breed A",
            address_street="123 Farm Lane",
            address_zip="12345",
            address_city="Farmville",
        )
        agricultural_holding_repository.add_holding(holding_candidate)

        finish_date = datetime.date.today()

        request_body = RequestBody(
            stallkarte_id=99999,  # Non-existent ID
            date_finished=finish_date,
        )

        with pytest.raises(HTTPException) as exc_info:
            handler(request_body, user, database)

        e = exc_info.value
        assert e.status_code == 404
        assert e.detail == "stallkarte ID '99999' not found"

    @staticmethod
    def test_raises_403_if_stallkarte_belongs_to_another_holding(
        database: Database,
        agricultural_holding_repository: AgriculturalHoldingRepository,
        stallkarte_repository: StallkarteRepository,
    ) -> None:
        # User 1
        user1 = domain.User(
            id="user1", firstname="Test", lastname="User", username="user1"
        )
        holding_candidate1 = AgriculturalHoldingCandidate(
            owner_user_id=user1.id,
            name="Farm 1",
            hatchery="Hatchery 1",
            eco_control_number="EC1",
            breed="Breed A",
            address_street="Street 1",
            address_zip="11111",
            address_city="City 1",
        )
        agricultural_holding_repository.add_holding(holding_candidate1)
        holding1 = agricultural_holding_repository.get_holding_by_owner(user1.id)

        assert holding1 is not None

        stallkarte = stallkarte_repository.create_stallkarte(holding1.id)

        # User 2
        user2 = domain.User(
            id="user2", firstname="Test", lastname="User", username="user2"
        )
        holding_candidate2 = AgriculturalHoldingCandidate(
            owner_user_id=user2.id,
            name="Farm 2",
            hatchery="Hatchery 2",
            eco_control_number="EC2",
            breed="Breed B",
            address_street="Street 2",
            address_zip="22222",
            address_city="City 2",
        )
        agricultural_holding_repository.add_holding(holding_candidate2)

        finish_date = datetime.date.today()

        # User 2 tries to finish User 1's stallkarte
        request_body = RequestBody(
            stallkarte_id=stallkarte.id,
            date_finished=finish_date,
        )

        with pytest.raises(HTTPException) as exc_info:
            handler(request_body, user2, database)

        e = exc_info.value
        assert e.status_code == 403
        assert (
            e.detail
            == f"stallkarte ID '{stallkarte.id}' does not belong to the user's holding"
        )
