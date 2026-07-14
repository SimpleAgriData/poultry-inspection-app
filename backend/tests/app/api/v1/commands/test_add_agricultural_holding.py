import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app import domain
from app.api.v1.commands.add_agricultural_holding import RequestBody, handler
from app.services.database import AgriculturalHoldingCandidate, Database
from app.services.database.repositories import AgriculturalHoldingRepository


class TestAddAgriculturalHolding:
    @staticmethod
    def test_add_agricultural_holding(
        database: Database,
        agricultural_holding_repository: AgriculturalHoldingRepository,
        user: domain.User,
    ) -> None:
        request_body = RequestBody(
            name="Sunny Farms",
            hatchery="Sunny Hatchery",
            eco_control_number="EC123456",
            breed="Breed A",
            address_street="123 Farm Lane",
            address_zip="12345",
            address_city="Farmville",
        )
        response = handler(request_body, user, database)

        assert (
            response.message == "Agricultural Holding 'Sunny Farms' added successfully"
        )

        holding = agricultural_holding_repository.get_holding_by_owner(user.id)

        assert holding is not None
        assert holding.name == "Sunny Farms"
        assert holding.hatchery == "Sunny Hatchery"
        assert holding.eco_control_number == "EC123456"
        assert holding.breed == "Breed A"
        assert holding.address_street == "123 Farm Lane"
        assert holding.address_zip == "12345"
        assert holding.address_city == "Farmville"

    @staticmethod
    def test_fails_if_user_already_has_holding(
        database: Database,
        agricultural_holding_repository: AgriculturalHoldingRepository,
        user: domain.User,
    ) -> None:
        existing_holding = AgriculturalHoldingCandidate(
            owner_user_id=user.id,
            name="Existing Farm",
            hatchery="Existing Hatchery",
            eco_control_number="EC654321",
            breed="Breed B",
            address_street="456 Existing Lane",
            address_zip="54321",
            address_city="Existingville",
        )
        agricultural_holding_repository.add_holding(existing_holding)

        request_body = RequestBody(
            name="New Farm",
            hatchery="New Hatchery",
            eco_control_number="EC111111",
            breed="Breed C",
            address_street="789 New Lane",
            address_zip="67890",
            address_city="Newville",
        )

        with pytest.raises(HTTPException) as exc_info:
            handler(request_body, user, database)

        assert exc_info.value.args[0] == 400
        assert (
            exc_info.value.args[1]
            == "user already has an associated agricultural holding"
        )

    @staticmethod
    def test_request_body_missing_fields(
        database: Database,
        agricultural_holding_repository: AgriculturalHoldingRepository,
    ) -> None:
        with pytest.raises(ValidationError) as exc_info:
            RequestBody(
                name="",
                hatchery="",
                eco_control_number="",
                breed="",
                address_street="",
                address_zip="",
                address_city="",
            )

        e = exc_info.value

        assert isinstance(e, ValidationError)

        errors = e.errors()
        assert len(errors) == 7
        assert errors[0]["loc"] == ("name",)
        assert errors[0]["msg"] == "String should have at least 1 character"

        assert errors[1]["loc"] == ("hatchery",)
        assert errors[1]["msg"] == "String should have at least 1 character"

        assert errors[2]["loc"] == ("eco_control_number",)
        assert errors[2]["msg"] == "String should have at least 1 character"

        assert errors[3]["loc"] == ("breed",)
        assert errors[3]["msg"] == "String should have at least 1 character"

        assert errors[4]["loc"] == ("address_street",)
        assert errors[4]["msg"] == "String should have at least 1 character"

        assert errors[5]["loc"] == ("address_zip",)
        assert errors[5]["msg"] == "String should have at least 1 character"

        assert errors[6]["loc"] == ("address_city",)
        assert errors[6]["msg"] == "String should have at least 1 character"
