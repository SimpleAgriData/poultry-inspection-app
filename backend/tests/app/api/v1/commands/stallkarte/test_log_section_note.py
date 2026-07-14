import pytest
from fastapi import HTTPException

from app import domain
from app.api.v1.commands.stallkarte.log_section_note import RequestBody, handler
from app.domain import AgriculturalHolding
from app.services.database import Database
from app.services.database.repositories import (
    StallkarteRepository,
)


class TestLogSectionNote:
    @staticmethod
    def test_log_section_note(
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

        farm = domain.Farm(
            id=1,
            name="Rearing Farm 1",
            type=domain.FarmType.REARING,
            vvvo_number="RF-001",
            sections=[],
            holding=holding_farms_5,
        )
        farm.sections = [
            domain.Section(id=1, name="Section 1", farm=farm),
        ]

        events = stallkarte.assign_rearing_farm(farm)

        for event in events:
            stallkarte_repository.add_event(stallkarte.id, event)

        request_body = RequestBody(
            stallkarte_id=stallkarte.id,
            production_day=1,
            section_number=1,
            note="Section note",
        )

        response = handler(request_body, user, database)

        assert response.message == "Section note logged successfully for section '1'"

        updated_stallkarte = stallkarte_repository.get_stallkarte_by_id(stallkarte.id)

        assert updated_stallkarte is not None
        assert len(updated_stallkarte.state.days) == 1
        day = updated_stallkarte.state.days[1]
        assert len(day.sections) == 1
        section = day.sections[1]
        assert section.note == "Section note"

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
            section_number=1,
            note="Section note",
        )

        with pytest.raises(HTTPException) as exc_info:
            handler(request_body, user, database)

        e = exc_info.value
        assert e.status_code == 403
