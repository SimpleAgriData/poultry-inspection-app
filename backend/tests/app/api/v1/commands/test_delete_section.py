import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app import domain
from app.api.v1.commands.delete_section import RequestBody, handler
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


class TestDeleteSection:
    @staticmethod
    def test_deletes_existing_section(
        database: Database,
        holding: AgriculturalHolding,
        farm_repository: FarmRepository,
        section_repository: SectionRepository,
        user: domain.User,
    ) -> None:
        farm = farm_repository.add_farm(
            holding.id,
            FarmCandidate(
                name="Main Farm",
                type=FarmTypeCandidate.FATTENING,
                vvvo_number="VV789012",
            ),
        )
        section = section_repository.add_section(
            farm.id,
            SectionCandidate(name="S1"),
        )

        response = handler(RequestBody(section_id=section.id), user, database)
        assert response.message == f"Section '{section.name}' deleted successfully"

        assert section_repository.get_section_by_id(section.id) is None

    @staticmethod
    def test_request_body_validation_errors() -> None:
        with pytest.raises(ValidationError) as exc_info:
            RequestBody(section_id=0)
        e = exc_info.value
        errors = e.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("section_id",)
        assert errors[0]["msg"] == "Input should be greater than 0"

    @staticmethod
    def test_raises_404_if_section_not_found(
        database: Database,
        user: domain.User,
    ) -> None:
        with pytest.raises(HTTPException) as exc_info:
            handler(RequestBody(section_id=9999), user, database)
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
                name="Main Farm",
                type=FarmTypeCandidate.FATTENING,
                vvvo_number="VV789012",
            ),
        )
        section = section_repository.add_section(
            farm.id,
            SectionCandidate(name="S1"),
        )
        with pytest.raises(HTTPException) as exc_info:
            handler(RequestBody(section_id=section.id), other, database)
        e = exc_info.value
        assert e.status_code == 403
        assert e.detail == f"missing permission to delete Section ID '{section.id}'"
