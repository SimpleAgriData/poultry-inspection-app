from app.domain import AgriculturalHolding
from app.services.database import (
    FarmCandidate,
    FarmTypeCandidate,
)
from app.services.database.repositories import (
    AgriculturalHoldingRepository,
    FarmRepository,
)


class TestFarmRepository:
    @staticmethod
    def test_create_farm(
        farm_repository: FarmRepository,
        holding: AgriculturalHolding,
        agricultural_holding_repository: AgriculturalHoldingRepository,
    ) -> None:
        farm_candidate = FarmCandidate(
            type=FarmTypeCandidate.FATTENING,
            name="Main Farm",
            vvvo_number="VVVO654321",
        )
        created_farm = farm_repository.add_farm(holding.id, farm_candidate)

        assert created_farm.id != 0
        assert created_farm.name == farm_candidate.name
        assert created_farm.type.name == farm_candidate.type.name
        assert created_farm.holding.id == holding.id
        assert created_farm.vvvo_number == farm_candidate.vvvo_number

        # Read back from the database to ensure it was saved correctly
        db_farm = farm_repository.get_farm_by_id(created_farm.id)
        assert db_farm is not None
        assert db_farm.id == created_farm.id
        assert db_farm.name == created_farm.name
        assert db_farm.type == created_farm.type
        assert db_farm.holding.id == created_farm.holding.id

        # Check that the farm is associated with the correct holding
        db_holding = agricultural_holding_repository.get_holding_by_id(holding.id)
        assert db_holding is not None
        assert len(db_holding.farms) == 1
        assert db_holding.farms[0].id == created_farm.id

    @staticmethod
    def test_update_farm(
        farm_repository: FarmRepository,
        holding: AgriculturalHolding,
    ) -> None:
        farm_candidate = FarmCandidate(
            type=FarmTypeCandidate.REARING,
            name="North Farm",
            vvvo_number="VVVO456789",
        )
        created_farm = farm_repository.add_farm(holding.id, farm_candidate)
        farm_id = created_farm.id

        # Now, update the farm
        updated_candidate = FarmCandidate(
            type=FarmTypeCandidate.FATTENING,
            name="North Farm Updated",
            vvvo_number="VVVO456789_UPDATED",
        )
        updated_farm = farm_repository.update_farm(farm_id, updated_candidate)

        assert updated_farm.id == farm_id
        assert updated_farm.name == updated_candidate.name
        assert updated_farm.type.name == updated_candidate.type.name
        assert updated_farm.holding.id == holding.id
        assert updated_farm.vvvo_number == updated_candidate.vvvo_number

        # Read back from the database to ensure it was updated correctly
        db_farm = farm_repository.get_farm_by_id(farm_id)
        assert db_farm is not None
        assert db_farm.id == updated_farm.id
        assert db_farm.name == updated_farm.name
        assert db_farm.type == updated_farm.type
        assert db_farm.holding.id == updated_farm.holding.id

    @staticmethod
    def test_get_farm_by_id(
        farm_repository: FarmRepository,
        holding: AgriculturalHolding,
    ) -> None:
        farm_candidate = FarmCandidate(
            type=FarmTypeCandidate.FATTENING,
            name="XYZ Farm Unit",
            vvvo_number="VVVOXYZ456",
        )
        created_farm = farm_repository.add_farm(holding.id, farm_candidate)

        farm_id = created_farm.id
        fetched_farm = farm_repository.get_farm_by_id(farm_id)
        assert fetched_farm is not None
        assert fetched_farm.id == created_farm.id
        assert fetched_farm.name == created_farm.name
        assert fetched_farm.type == created_farm.type
        assert fetched_farm.holding.id == created_farm.holding.id
        assert fetched_farm.vvvo_number == created_farm.vvvo_number

    @staticmethod
    def test_get_farm_by_id_not_found(
        farm_repository: FarmRepository,
    ) -> None:
        non_existent_id = 999999
        fetched_farm = farm_repository.get_farm_by_id(non_existent_id)
        assert fetched_farm is None

    @staticmethod
    def test_delete_farm(
        farm_repository: FarmRepository,
        holding: AgriculturalHolding,
    ) -> None:
        farm_candidate = FarmCandidate(
            type=FarmTypeCandidate.REARING,
            name="East Farm",
            vvvo_number="VVVOABC456",
        )
        created_farm = farm_repository.add_farm(holding.id, farm_candidate)
        farm_id = created_farm.id
        farm_repository.delete_farm(farm_id)

        deleted_farm = farm_repository.get_farm_by_id(farm_id)
        assert deleted_farm is None

        soft_deleted_farm = farm_repository.get_farm_by_id(
            farm_id, include_deleted=True
        )
        assert soft_deleted_farm is not None
        assert soft_deleted_farm.id == farm_id

    @staticmethod
    def test_deleted_farm_does_not_appear_in_holding_farms(
        farm_repository: FarmRepository,
        holding: AgriculturalHolding,
        agricultural_holding_repository: AgriculturalHoldingRepository,
    ) -> None:
        farm_candidate = FarmCandidate(
            type=FarmTypeCandidate.FATTENING,
            name="West Farm",
            vvvo_number="VVVODEF456",
        )
        created_farm = farm_repository.add_farm(holding.id, farm_candidate)
        farm_id = created_farm.id

        farm_repository.delete_farm(farm_id)

        db_holding = agricultural_holding_repository.get_holding_by_id(holding.id)

        assert db_holding is not None
        assert db_holding.farms == []
