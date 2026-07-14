from app import domain
from app.api.v1.queries.find_my_agricultural_holding import (
    handler,
)
from app.domain import AgriculturalHolding
from app.services.database import (
    Database,
    FarmCandidate,
    FarmTypeCandidate,
    SectionCandidate,
)
from app.services.database.repositories import (
    FarmRepository,
    SectionRepository,
)


class TestFindMyAgriculturalHolding:
    @staticmethod
    def test_retrieves_holding_for_authenticated_user(
        database: Database,
        holding: AgriculturalHolding,
        farm_repository: FarmRepository,
        section_repository: SectionRepository,
        user: domain.User,
    ) -> None:
        farm = farm_repository.add_farm(
            holding.id,
            FarmCandidate(
                type=FarmTypeCandidate.FATTENING,
                name="Main Farm",
                vvvo_number="VV789012",
            ),
        )

        section = section_repository.add_section(
            farm.id,
            SectionCandidate(
                name="Section 1",
            ),
        )

        response = handler(db=database, user=user)

        response_holding = response.holding

        assert response_holding is not None

        assert response_holding.id == holding.id
        assert response_holding.name == holding.name
        assert len(response_holding.farms) == 1

        response_farm = response_holding.farms[0]
        assert response_farm.id == farm.id
        assert response_farm.name == farm.name

        assert len(response_farm.sections) == 1
        response_section = response_farm.sections[0]
        assert response_section.id == section.id
        assert response_section.name == section.name

    @staticmethod
    def test_returns_none_if_user_has_no_associated_holding(
        database: Database,
    ) -> None:
        user = domain.User(
            id="user_without_holding",
            firstname="Test",
            lastname="User",
            username="nonexistent_user",
        )

        response = handler(db=database, user=user)

        assert response.holding is None
