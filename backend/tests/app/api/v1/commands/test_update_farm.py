import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app import domain
from app.api.v1.commands.update_farm import RequestBody, RequestBodyFarmType, handler
from app.domain import AgriculturalHolding
from app.services.database import (
    Database,
    FarmCandidate,
    FarmTypeCandidate,
)
from app.services.database.repositories import (
    FarmRepository,
)


class TestUpdateFarm:
    @staticmethod
    def test_updates_existing_farm(
        database: Database,
        holding: AgriculturalHolding,
        farm_repository: FarmRepository,
        user: domain.User,
    ) -> None:
        farm = farm_repository.add_farm(
            holding.id,
            FarmCandidate(
                name="Old Farm",
                type=FarmTypeCandidate.FATTENING,
                vvvo_number="VV789012-OLD",
            ),
        )

        request_body = RequestBody(
            farm_id=farm.id,
            name="New Farm",
            type=RequestBodyFarmType.REARING,
            vvvo_number="VV789012-NEW",
        )

        response = handler(request_body, user, database)
        assert response.message == "Farm 'New Farm' updated successfully"

        updated = farm_repository.get_farm_by_id(farm.id)
        assert updated is not None
        assert updated.name == "New Farm"
        assert updated.type.name == RequestBodyFarmType.REARING.name
        assert updated.holding.id == holding.id
        assert updated.vvvo_number == "VV789012-NEW"

    @staticmethod
    def test_request_body_missing_fields() -> None:
        with pytest.raises(ValidationError) as exc_info:
            RequestBody(
                farm_id=0,
                name="",
                type="abc",  # type: ignore[arg-type]
                vvvo_number="",
            )
        e = exc_info.value
        assert isinstance(e, ValidationError)
        errors = e.errors()
        assert len(errors) == 4
        assert errors[0]["loc"] == ("farm_id",)
        assert errors[0]["msg"] == "Input should be greater than 0"
        assert errors[1]["loc"] == ("name",)
        assert errors[1]["msg"] == "String should have at least 1 character"
        assert errors[2]["loc"] == ("type",)
        assert (
            errors[2]["msg"] == "Input should be 'fattening', 'rearing' or 'combined'"
        )
        assert errors[3]["loc"] == ("vvvo_number",)
        assert errors[3]["msg"] == "String should have at least 1 character"

    @staticmethod
    def test_raises_404_if_farm_not_found(
        database: Database,
        user: domain.User,
    ) -> None:
        request_body = RequestBody(
            farm_id=9999,
            name="New Farm",
            type=RequestBodyFarmType.REARING,
            vvvo_number="VV789012",
        )
        with pytest.raises(HTTPException) as exc_info:
            handler(request_body, user, database)
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
            id="otheruser", firstname="Other", lastname="User", username="now_owner"
        )
        farm = farm_repository.add_farm(
            holding.id,
            FarmCandidate(
                name="Old Farm",
                type=FarmTypeCandidate.FATTENING,
                vvvo_number="VV789012",
            ),
        )
        request_body = RequestBody(
            farm_id=farm.id,
            name="New Farm",
            type=RequestBodyFarmType.REARING,
            vvvo_number="VV789012",
        )
        with pytest.raises(HTTPException) as exc_info:
            handler(request_body, other, database)
        e = exc_info.value
        assert e.status_code == 403
        assert e.detail == f"missing permission to update Farm ID '{farm.id}'"
