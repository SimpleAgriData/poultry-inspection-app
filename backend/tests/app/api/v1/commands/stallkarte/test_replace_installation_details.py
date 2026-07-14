import datetime

import pytest
from fastapi import HTTPException

from app import domain
from app.api.v1.commands.stallkarte.replace_installation_details import (
    RequestBody,
    RequestBodyParentFlockEntry,
    RequestBodySectionInstallationDetails,
    handler,
)
from app.domain import AgriculturalHolding, StallkarteAggregator
from app.services.database import Database
from app.services.database.repositories import (
    FarmCandidate,
    FarmRepository,
    FarmTypeCandidate,
    SectionCandidate,
    SectionRepository,
    StallkarteRepository,
)


class TestReplaceInstallationDetails:
    @staticmethod
    def test_replace_installation_details(
        database: Database,
        stallkarte_repository: StallkarteRepository,
        holding_farms_5: AgriculturalHolding,
        farm_repository: FarmRepository,
        section_repository: SectionRepository,
    ) -> None:
        user = domain.User(
            firstname="Test",
            lastname="User",
            id=holding_farms_5.owner_user_id,
            username="testuser",
        )
        stallkarte = stallkarte_repository.create_stallkarte(holding_farms_5.id)

        db_farm = farm_repository.add_farm(
            holding_farms_5.id,
            FarmCandidate(
                type=FarmTypeCandidate.REARING,
                name="Rearing Farm",
                vvvo_number="VV999001",
            ),
        )
        section_repository.add_section(db_farm.id, SectionCandidate(name="Section 1"))
        section_repository.add_section(db_farm.id, SectionCandidate(name="Section 2"))
        rearing_farm = farm_repository.get_farm_by_id(db_farm.id)
        if rearing_farm is None:
            raise ValueError("rearing farm not found")

        start_events = stallkarte.start_stallkarte(
            date_started=datetime.date.today(),
            date_hatched=datetime.date.today(),
            hatchery_name="Hatchery",
            breed="A1",
            fattening_cycle="42",
            eco_control_number="123321",
            is_eu_bio=True,
            is_naturland=False,
        )
        stallkarte_repository.add_events(stallkarte.id, start_events)
        StallkarteAggregator.apply_to(stallkarte, [rearing_farm], start_events)

        assign_events = stallkarte.assign_rearing_farm(rearing_farm)
        stallkarte_repository.add_events(stallkarte.id, assign_events)
        StallkarteAggregator.apply_to(stallkarte, [rearing_farm], assign_events)

        request_body = RequestBody(
            stallkarte_id=stallkarte.id,
            section_details=[
                RequestBodySectionInstallationDetails(
                    section_number=1,
                    initial_animals_count=4100,
                    initial_weight_grams=45,
                    bedding="Strohhäcksel",
                    parent_flocks=[
                        RequestBodyParentFlockEntry(
                            herd_identifier="ET-1",
                            production_week=5,
                        ),
                        RequestBodyParentFlockEntry(
                            herd_identifier="ET-2",
                            production_week=10,
                        ),
                    ],
                ),
                RequestBodySectionInstallationDetails(
                    section_number=2,
                    initial_animals_count=3900,
                    initial_weight_grams=44,
                    bedding="Strohhäcksel",
                    parent_flocks=[
                        RequestBodyParentFlockEntry(
                            herd_identifier="ET-2",
                            production_week=10,
                        )
                    ],
                ),
            ],
        )

        response = handler(request_body, user, database)

        assert response.message == "Installation details replaced successfully"

        updated_stallkarte = stallkarte_repository.get_stallkarte_by_id(stallkarte.id)
        assert updated_stallkarte is not None

        section_1 = updated_stallkarte.state.installation_details_by_section[1]
        assert section_1.initial_animals_count == 4100
        assert section_1.initial_weight_grams == 45
        assert section_1.bedding == "Strohhäcksel"
        assert len(section_1.parent_flocks) == 2

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
            section_details=[],
        )

        with pytest.raises(HTTPException) as exc_info:
            handler(request_body, user, database)

        e = exc_info.value
        assert e.status_code == 403
