import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app import domain
from app.api.v1.commands.update_agricultural_holding import RequestBody, handler
from app.services.database import AgriculturalHoldingCandidate, Database
from app.services.database.repositories import AgriculturalHoldingRepository


class TestUpdateAgriculturalHolding:
    @staticmethod
    def test_updates_existing_holding(
        database: Database,
        agricultural_holding_repository: AgriculturalHoldingRepository,
        user: domain.User,
    ) -> None:
        created = agricultural_holding_repository.add_holding(
            AgriculturalHoldingCandidate(
                owner_user_id=user.id,
                name="Old Name",
                hatchery="Old Hatchery",
                eco_control_number="EC-OLD",
                breed="Old Breed",
                address_street="Old Street 1",
                address_zip="00000",
                address_city="Oldtown",
            )
        )

        request = RequestBody(
            holding_id=created.id,
            name="New Name",
            hatchery="New Hatchery",
            eco_control_number="EC-NEW",
            breed="New Breed",
            address_street="New Street 2",
            address_zip="99999",
            address_city="Newcity",
        )

        response = handler(request, user, database)
        assert (
            response.message == "Agricultural Holding 'New Name' updated successfully"
        )

        updated = agricultural_holding_repository.get_holding_by_id(created.id)
        assert updated is not None
        assert updated.name == "New Name"
        assert updated.hatchery == "New Hatchery"
        assert updated.eco_control_number == "EC-NEW"
        assert updated.breed == "New Breed"
        assert updated.address_street == "New Street 2"
        assert updated.address_zip == "99999"
        assert updated.address_city == "Newcity"

    @staticmethod
    def test_request_body_validation_errors() -> None:
        with pytest.raises(ValidationError) as exc_info:
            RequestBody(
                holding_id=0,
                name="",
                hatchery="",
                eco_control_number="",
                breed="",
                address_street="",
                address_zip="",
                address_city="",
            )
        errors = exc_info.value.errors()
        assert len(errors) == 8
        by_loc = {e["loc"][0]: e["msg"] for e in errors}
        assert by_loc["holding_id"] == "Input should be greater than 0"
        assert by_loc["name"] == "String should have at least 1 character"
        assert by_loc["hatchery"] == "String should have at least 1 character"
        assert by_loc["eco_control_number"] == "String should have at least 1 character"
        assert by_loc["breed"] == "String should have at least 1 character"
        assert by_loc["address_street"] == "String should have at least 1 character"
        assert by_loc["address_zip"] == "String should have at least 1 character"
        assert by_loc["address_city"] == "String should have at least 1 character"

    @staticmethod
    def test_raises_404_if_holding_not_found(
        database: Database,
        user: domain.User,
    ) -> None:
        request = RequestBody(
            holding_id=9999,
            name="New Name",
            hatchery="New Hatchery",
            eco_control_number="EC-NEW",
            breed="New Breed",
            address_street="New Street 2",
            address_zip="99999",
            address_city="Newcity",
        )
        with pytest.raises(HTTPException) as exc_info:
            handler(request, user, database)
        e = exc_info.value
        assert e.status_code == 404
        assert e.detail == "Agricultural Holding ID '9999' not found"

    @staticmethod
    def test_raises_403_if_user_not_owner(
        database: Database,
        agricultural_holding_repository: AgriculturalHoldingRepository,
        user: domain.User,
    ) -> None:
        other = domain.User(
            id="otheruser", firstname="Other", lastname="User", username="other"
        )
        created = agricultural_holding_repository.add_holding(
            AgriculturalHoldingCandidate(
                owner_user_id=user.id,
                name="Old Name",
                hatchery="Old Hatchery",
                eco_control_number="EC-OLD",
                breed="Old Breed",
                address_street="Old Street 1",
                address_zip="00000",
                address_city="Oldtown",
            )
        )
        request = RequestBody(
            holding_id=created.id,
            name="New Name",
            hatchery="New Hatchery",
            eco_control_number="EC-NEW",
            breed="New Breed",
            address_street="New Street 2",
            address_zip="99999",
            address_city="Newcity",
        )
        with pytest.raises(HTTPException) as exc_info:
            handler(request, other, database)
        e = exc_info.value
        assert e.status_code == 403
        assert (
            e.detail
            == f"Missing permission to update Agricultural Holding ID '{created.id}'"
        )
