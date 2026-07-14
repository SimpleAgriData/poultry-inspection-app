import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app import domain
from app.api.v1.commands.add_farm import RequestBody, RequestBodyFarmType, handler
from app.domain import AgriculturalHolding
from app.services.database import Database
from app.services.database.repositories import (
    AgriculturalHoldingRepository,
    FarmRepository,
)


class TestAddFarm:
    @staticmethod
    def test_add_farm(
        database: Database,
        holding: AgriculturalHolding,
        agricultural_holding_repository: AgriculturalHoldingRepository,
        farm_repository: FarmRepository,
        user: domain.User,
    ) -> None:
        request_body = RequestBody(
            name="Main Farm",
            type=RequestBodyFarmType.REARING,
            agricultural_holding_id=holding.id,
            vvvo_number="VV789012",
        )

        response = handler(request_body, user, database)

        assert response.message == "Farm 'Main Farm' added successfully"

        db_holding = agricultural_holding_repository.get_holding_by_id(holding.id)
        assert db_holding is not None
        assert len(db_holding.farms) == 1
        farm = db_holding.farms[0]
        assert farm.name == "Main Farm"
        assert farm.type.name == RequestBodyFarmType.REARING.name
        assert farm.holding.id == holding.id
        assert farm.vvvo_number == "VV789012"

        fetched_farm = farm_repository.get_farm_by_id(farm.id)
        assert fetched_farm is not None
        assert fetched_farm.id == farm.id
        assert fetched_farm.name == farm.name

    @staticmethod
    def test_request_body_missing_fields(
        database: Database,
        agricultural_holding_repository: AgriculturalHoldingRepository,
    ) -> None:
        with pytest.raises(ValidationError) as exc_info:
            RequestBody(
                name="",
                type="abc",  # type: ignore[arg-type]
                agricultural_holding_id=0,
                vvvo_number="",
            )

        e = exc_info.value

        assert isinstance(e, ValidationError)

        errors = e.errors()
        assert len(errors) == 4
        assert errors[0]["loc"] == ("name",)
        assert errors[0]["msg"] == "String should have at least 1 character"

        assert errors[1]["loc"] == ("type",)
        assert (
            errors[1]["msg"] == "Input should be 'fattening', 'rearing' or 'combined'"
        )

        assert errors[2]["loc"] == ("vvvo_number",)
        assert errors[2]["msg"] == "String should have at least 1 character"

        assert errors[3]["loc"] == ("agricultural_holding_id",)
        assert errors[3]["msg"] == "Input should be greater than 0"

    @staticmethod
    def test_raises_404_if_holding_not_found(
        database: Database,
        farm_repository: FarmRepository,
        user: domain.User,
    ) -> None:
        request_body = RequestBody(
            name="Main Farm",
            type=RequestBodyFarmType.REARING,
            agricultural_holding_id=9999,
            vvvo_number="VV789012",
        )

        with pytest.raises(HTTPException) as exc_info:
            handler(request_body, user, database)

        e = exc_info.value

        assert e.status_code == 404
        assert e.detail == "Agricultural Holding ID '9999' not found"

    @staticmethod
    def test_raises_403_if_user_not_owner(
        database: Database,
        holding: AgriculturalHolding,
    ) -> None:
        other_user = domain.User(
            id="otheruser", firstname="Other", lastname="User", username="otheruser"
        )

        request_body = RequestBody(
            name="Main Farm",
            type=RequestBodyFarmType.REARING,
            agricultural_holding_id=holding.id,
            vvvo_number="VV789012",
        )

        with pytest.raises(HTTPException) as exc_info:
            handler(request_body, other_user, database)

        e = exc_info.value
        assert e.status_code == 403
        assert (
            e.detail == f"Missing permission to add Farm to "
            f"Agricultural Holding ID '{holding.id}'"
        )
