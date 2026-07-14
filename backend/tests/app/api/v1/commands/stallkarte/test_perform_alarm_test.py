import pytest
from fastapi import HTTPException

from app import domain
from app.api.v1.commands.stallkarte.perform_alarm_test import (
    RequestBody,
    handler,
)
from app.domain import StallkarteCycle
from app.services.database import Database
from app.services.database.repositories import StallkarteRepository


class TestPerformAlarmTest:
    @staticmethod
    def test_perform_alarm_test(
        database: Database,
        stallkarte_repository: StallkarteRepository,
        holding: domain.AgriculturalHolding,
        user: domain.User,
    ) -> None:
        stallkarte = stallkarte_repository.create_stallkarte(holding.id)

        request_body = RequestBody(
            stallkarte_id=stallkarte.id,
            cycle=StallkarteCycle.REARING,
            did_alarm_test=True,
            did_emergency_power_test=False,
        )

        response = handler(request_body, user, database)

        assert (
            response.message == "Alarm test performed successfully for cycle 'rearing'"
        )

        updated_stallkarte = stallkarte_repository.get_stallkarte_by_id(stallkarte.id)

        assert updated_stallkarte is not None
        assert updated_stallkarte.state.rearing_checklist is not None
        checklist = updated_stallkarte.state.rearing_checklist
        assert checklist.alarm_test.did_alarm_test is True
        assert checklist.alarm_test.did_emergency_power_test is False

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
            cycle=StallkarteCycle.REARING,
            did_alarm_test=True,
            did_emergency_power_test=False,
        )

        with pytest.raises(HTTPException) as exc_info:
            handler(request_body, user, database)

        e = exc_info.value
        assert e.status_code == 403
