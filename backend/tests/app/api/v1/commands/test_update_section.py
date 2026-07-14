import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app import domain
from app.api.v1.commands.update_section import RequestBody, handler
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


class TestUpdateSection:
    @staticmethod
    def test_updates_existing_section(
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
            SectionCandidate(name="Section 1"),
        )

        request_body = RequestBody(section_id=section.id, name="Section 2")

        response = handler(request_body, user, database)
        assert response.message == "Section 'Section 2' updated successfully"

        updated = section_repository.get_section_by_id(section.id)
        assert updated is not None
        assert updated.name == "Section 2"
        assert updated.farm.id == farm.id

    @staticmethod
    def test_request_body_missing_fields() -> None:
        with pytest.raises(ValidationError) as exc_info:
            RequestBody(
                section_id=-1,
                name="",
            )
        e = exc_info.value
        errors = e.errors()
        assert len(errors) == 2
        assert errors[0]["loc"] == ("section_id",)
        assert errors[0]["msg"] == "Input should be greater than 0"
        assert errors[1]["loc"] == ("name",)
        assert errors[1]["msg"] == "String should have at least 1 character"

    @staticmethod
    def test_raises_404_if_section_not_found(
        database: Database,
        user: domain.User,
    ) -> None:
        request_body = RequestBody(section_id=9999, name="Section 2")
        with pytest.raises(HTTPException) as exc_info:
            handler(request_body, user, database)
        e = exc_info.value
        assert e.status_code == 404
        assert e.detail == "section ID '9999' not found"

    @staticmethod
    def test_raises_403_if_user_not_owner(
        database: Database,
        holding: AgriculturalHolding,
        farm_repository: FarmRepository,
        section_repository: SectionRepository,
    ) -> None:
        other = domain.User(
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
        section = section_repository.add_section(
            farm.id,
            SectionCandidate(name="Section 1"),
        )
        request_body = RequestBody(section_id=section.id, name="Section 2")
        with pytest.raises(HTTPException) as exc_info:
            handler(request_body, other, database)
        e = exc_info.value
        assert e.status_code == 403
        assert e.detail == f"missing permission to update Section ID '{section.id}'"
