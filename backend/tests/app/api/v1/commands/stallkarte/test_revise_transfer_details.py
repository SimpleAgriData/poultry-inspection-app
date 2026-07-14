import datetime

import pytest
from fastapi import HTTPException

from app import domain
from app.api.v1.commands.stallkarte.revise_transfer_details import RequestBody, handler
from app.domain import AgriculturalHolding
from app.domain.stallkarte.stallkarte_state import StallkarteCycle
from app.services.database import Database
from app.services.database.repositories import (
    StallkarteRepository,
)


class TestReviseTransferDetails:
    @staticmethod
    def test_revise_transfer_details(
        database: Database,
        stallkarte_repository: StallkarteRepository,
        user: domain.User,
        holding: domain.AgriculturalHolding,
    ) -> None:
        stallkarte = stallkarte_repository.create_stallkarte(holding.id)

        farm = domain.Farm(
            holding=holding,
            id=1,
            vvvo_number="VV100000",
            name="Rearing Farm 1",
            type=domain.FarmType.FATTENING,
            sections=[],
        )
        farm.sections = [
            domain.Section(
                id=1,
                name="Section 1",
                farm=farm,
            ),
            domain.Section(
                id=2,
                name="Section 2",
                farm=farm,
            ),
        ]

        aggregator = domain.StallkarteAggregator(stallkarte, {farm.id: farm})

        today = datetime.date.today()
        events = stallkarte.start_stallkarte(
            date_started=today,
            date_hatched=today,
            hatchery_name="Hatchery",
            breed="A1",
            fattening_cycle="42",
            eco_control_number="123321",
            is_eu_bio=True,
            is_naturland=False,
        )
        aggregator.apply_all(events)
        stallkarte_repository.add_events(stallkarte.id, events)

        events = stallkarte.assign_fattening_farm(farm)
        aggregator.apply_all(events)
        stallkarte_repository.add_events(stallkarte.id, events)

        events = stallkarte.transfer_flock(today, {1: 100, 2: 100})
        stallkarte_repository.add_events(stallkarte.id, events)

        request_body = RequestBody(
            stallkarte_id=stallkarte.id,
            animals_by_section_number={1: 90, 2: 110},
        )

        response = handler(request_body, user, database)

        assert response.message == "Transfer details revised successfully"

        updated_stallkarte = stallkarte_repository.get_stallkarte_by_id(stallkarte.id)

        assert updated_stallkarte is not None
        assert updated_stallkarte.state.current_cycle == StallkarteCycle.FATTENING
        assert updated_stallkarte.state.transfer is not None
        assert updated_stallkarte.state.transfer.date == today
        assert updated_stallkarte.state.transfer.production_day == 0
        assert updated_stallkarte.state.transfer.animals_by_section_number == {
            1: 90,
            2: 110,
        }

    @staticmethod
    def test_raises_403_if_stallkarte_not_owned(
        database: Database,
        stallkarte_repository: StallkarteRepository,
        holding_farms_5: AgriculturalHolding,
        other_holding: domain.AgriculturalHolding,
        user: domain.User,
    ) -> None:
        other_stallkarte = stallkarte_repository.create_stallkarte(other_holding.id)

        request_body = RequestBody(
            stallkarte_id=other_stallkarte.id,
            animals_by_section_number={1: 100},
        )

        with pytest.raises(HTTPException) as exc_info:
            handler(request_body, user, database)

        e = exc_info.value
        assert e.status_code == 403
