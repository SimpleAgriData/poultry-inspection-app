import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app import domain
from app.api.v1.commands.add_section import RequestBody, handler
from app.domain import AgriculturalHolding
from app.services.database import (
    Database,
    FarmCandidate,
    FarmTypeCandidate,
)
from app.services.database.repositories import (
    FarmRepository,
    SectionRepository,
)


class TestAddSection:
    @staticmethod
    def test_add_section(
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

        request_body = RequestBody(name="Section 1", farm_id=farm.id)

        response = handler(request_body, user, database)

        assert response.message == "Section 'Section 1' added successfully"

        fetched_farm = farm_repository.get_farm_by_id(farm.id)
        assert fetched_farm is not None
        assert len(fetched_farm.sections) == 1
        section = fetched_farm.sections[0]
        assert section.name == "Section 1"
        assert section.farm.id == farm.id

        fetched_section = section_repository.get_section_by_id(section.id)
        assert fetched_section is not None
        assert fetched_section.id == section.id
        assert fetched_section.name == section.name

    @staticmethod
    def test_request_body_missing_fields(
        database: Database,
        holding: AgriculturalHolding,
        farm_repository: FarmRepository,
    ) -> None:
        with pytest.raises(ValidationError) as exc_info:
            RequestBody(
                name="",
                farm_id=-1,
            )

        e = exc_info.value

        assert isinstance(e, ValidationError)

        errors = e.errors()
        assert len(errors) == 2

        assert errors[0]["loc"] == ("name",)
        assert errors[0]["msg"] == "String should have at least 1 character"

        assert errors[1]["loc"] == ("farm_id",)
        assert errors[1]["msg"] == "Input should be greater than 0"

    @staticmethod
    def test_raises_404_if_farm_not_found(
        database: Database,
        user: domain.User,
    ) -> None:
        request_body = RequestBody(name="Section 1", farm_id=9999)

        with pytest.raises(HTTPException) as exc_info:
            handler(request_body, user, database)

        e = exc_info.value

        assert e.status_code == 404
        assert e.detail == "Farm ID '9999' not found"

    @staticmethod
    def test_raises_403_if_user_not_owner(
        database: Database,
        holding: AgriculturalHolding,
        farm_repository: FarmRepository,
    ) -> None:
        other_user = domain.User(
            id="otheruser", firstname="Other", lastname="User", username="not_owner"
        )

        farm = farm_repository.add_farm(
            holding.id,
            FarmCandidate(
                type=FarmTypeCandidate.FATTENING,
                name="Main Farm",
                vvvo_number="VV789012",
            ),
        )

        request_body = RequestBody(name="Section 1", farm_id=farm.id)
        with pytest.raises(HTTPException) as exc_info:
            handler(request_body, other_user, database)

        e = exc_info.value

        assert e.status_code == 403
        assert e.detail == f"Missing permission to add Section to Farm ID '{farm.id}'"
