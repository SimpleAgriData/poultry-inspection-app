import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app import domain
from app.api.v1.commands.delete_farm import RequestBody, handler
from app.domain import AgriculturalHolding
from app.services.database import (
    Database,
    FarmCandidate,
    FarmTypeCandidate,
)
from app.services.database.repositories import (
    FarmRepository,
)


class TestDeleteFarm:
    @staticmethod
    def test_deletes_existing_farm(
        database: Database,
        holding: AgriculturalHolding,
        farm_repository: FarmRepository,
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

        response = handler(RequestBody(farm_id=farm.id), user, database)
        assert response.message == f"Farm '{farm.name}' deleted successfully"

        assert farm_repository.get_farm_by_id(farm.id) is None

    @staticmethod
    def test_request_body_validation_errors() -> None:
        with pytest.raises(ValidationError) as exc_info:
            RequestBody(farm_id=0)
        e = exc_info.value
        errors = e.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("farm_id",)
        assert errors[0]["msg"] == "Input should be greater than 0"

    @staticmethod
    def test_raises_404_if_farm_not_found(
        database: Database,
        user: domain.User,
    ) -> None:
        with pytest.raises(HTTPException) as exc_info:
            handler(RequestBody(farm_id=9999), user, database)
        e = exc_info.value
        assert e.status_code == 404
        assert e.detail == "farm ID '9999' not found"

    @staticmethod
    def test_raises_403_if_user_not_owner(
        database: Database,
        holding: AgriculturalHolding,
        farm_repository: FarmRepository,
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
        with pytest.raises(HTTPException) as exc_info:
            handler(RequestBody(farm_id=farm.id), other, database)
        e = exc_info.value
        assert e.status_code == 403
        assert e.detail == f"missing permission to delete Farm ID '{farm.id}'"
