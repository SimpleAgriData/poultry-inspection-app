from app.domain import AgriculturalHolding
from app.services.database import (
    FarmCandidate,
    FarmTypeCandidate,
    SectionCandidate,
)
from app.services.database.repositories import (
    FarmRepository,
    SectionRepository,
)


class TestSectionRepository:
    @staticmethod
    def test_create_section(
        section_repository: SectionRepository,
        farm_repository: FarmRepository,
        holding: AgriculturalHolding,
    ) -> None:
        farm_candidate = FarmCandidate(
            type=FarmTypeCandidate.FATTENING,
            name="Main Farm",
            vvvo_number="VVVO654321",
        )
        farm = farm_repository.add_farm(holding.id, farm_candidate)

        section_candidate = SectionCandidate(name="Section 1")
        created_section = section_repository.add_section(farm.id, section_candidate)

        assert created_section.id != 0
        assert created_section.name == section_candidate.name
        assert created_section.farm.id == farm.id

        # Read back from the database to ensure it was saved correctly
        db_section = section_repository.get_section_by_id(created_section.id)
        assert db_section is not None
        assert db_section.id == created_section.id
        assert db_section.name == created_section.name
        assert db_section.farm.id == created_section.farm.id

    @staticmethod
    def test_update_section(
        section_repository: SectionRepository,
        farm_repository: FarmRepository,
        holding: AgriculturalHolding,
    ) -> None:
        farm_candidate = FarmCandidate(
            type=FarmTypeCandidate.REARING,
            name="North Farm",
            vvvo_number="VVVO456789",
        )
        farm = farm_repository.add_farm(holding.id, farm_candidate)

        section_candidate = SectionCandidate(name="Section 2")
        created_section = section_repository.add_section(farm.id, section_candidate)
        section_id = created_section.id

        # Now, update the section
        updated_candidate = SectionCandidate(name="Section 2 Updated")
        updated_section = section_repository.update_section(
            section_id, updated_candidate
        )

        assert updated_section.id == section_id
        assert updated_section.name == updated_candidate.name
        assert updated_section.farm.id == farm.id

        # Read back from the database to ensure it was updated correctly
        db_section = section_repository.get_section_by_id(section_id)
        assert db_section is not None
        assert db_section.id == updated_section.id
        assert db_section.name == updated_section.name
        assert db_section.farm.id == updated_section.farm.id

    @staticmethod
    def test_get_section_by_id(
        section_repository: SectionRepository,
        farm_repository: FarmRepository,
        holding: AgriculturalHolding,
    ) -> None:
        farm_candidate = FarmCandidate(
            type=FarmTypeCandidate.FATTENING,
            name="XYZ Farm Unit",
            vvvo_number="VVVOXYZ456",
        )
        farm = farm_repository.add_farm(holding.id, farm_candidate)

        section_candidate = SectionCandidate(name="Section X")
        created_section = section_repository.add_section(farm.id, section_candidate)

        section_id = created_section.id
        fetched_section = section_repository.get_section_by_id(section_id)
        assert fetched_section is not None
        assert fetched_section.id == created_section.id
        assert fetched_section.name == created_section.name
        assert fetched_section.farm.id == created_section.farm.id

    @staticmethod
    def test_get_section_by_id_not_found(
        section_repository: SectionRepository,
    ) -> None:
        non_existent_id = 999999
        fetched_section = section_repository.get_section_by_id(non_existent_id)
        assert fetched_section is None

    @staticmethod
    def test_delete_section(
        section_repository: SectionRepository,
        farm_repository: FarmRepository,
        holding: AgriculturalHolding,
    ) -> None:
        farm_candidate = FarmCandidate(
            type=FarmTypeCandidate.REARING,
            name="ABC Farm Unit",
            vvvo_number="VVVOABC456",
        )
        farm = farm_repository.add_farm(holding.id, farm_candidate)

        section_candidate = SectionCandidate(name="Section Y")
        created_section = section_repository.add_section(farm.id, section_candidate)
        section_id = created_section.id
        section_repository.delete_section(section_id)

        deleted_section = section_repository.get_section_by_id(section_id)
        assert deleted_section is None

        soft_deleted_section = section_repository.get_section_by_id(
            section_id, include_deleted=True
        )
        assert soft_deleted_section is not None
        assert soft_deleted_section.id == section_id

    @staticmethod
    def test_deleted_section_does_not_appear_in_farm(
        section_repository: SectionRepository,
        farm_repository: FarmRepository,
        holding: AgriculturalHolding,
    ) -> None:
        farm_candidate = FarmCandidate(
            type=FarmTypeCandidate.FATTENING,
            name="DEF Farm Unit",
            vvvo_number="VVVODEF012",
        )
        farm = farm_repository.add_farm(holding.id, farm_candidate)

        section_candidate = SectionCandidate(name="Section Z")
        created_section = section_repository.add_section(farm.id, section_candidate)
        section_id = created_section.id

        section_repository.delete_section(section_id)

        db_farm = farm_repository.get_farm_by_id(farm.id)
        assert db_farm is not None
        assert db_farm.sections == []
