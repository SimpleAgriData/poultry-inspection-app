from app.services.database import AgriculturalHoldingCandidate
from app.services.database.repositories import AgriculturalHoldingRepository


class TestAgriculturalHoldingRepository:
    @staticmethod
    def test_create_agricultural_holding(
        agricultural_holding_repository: AgriculturalHoldingRepository,
    ) -> None:
        holding_candidate = AgriculturalHoldingCandidate(
            owner_user_id="farmer_john",
            name="Sunny Farm",
            hatchery="Happy Hatchery",
            eco_control_number="EC123456",
            breed="Lohmann Brown",
            address_street="123 Farm Lane",
            address_zip="12345",
            address_city="Farmville",
        )
        created_holding = agricultural_holding_repository.add_holding(holding_candidate)

        assert created_holding.id != 0
        assert created_holding.owner_user_id == holding_candidate.owner_user_id
        assert created_holding.name == holding_candidate.name
        assert created_holding.hatchery == holding_candidate.hatchery
        assert (
            created_holding.eco_control_number == holding_candidate.eco_control_number
        )
        assert created_holding.breed == holding_candidate.breed
        assert created_holding.address_street == holding_candidate.address_street
        assert created_holding.address_zip == holding_candidate.address_zip
        assert created_holding.address_city == holding_candidate.address_city

        # Read back from the database to ensure it was saved correctly
        db_holding = agricultural_holding_repository.get_holding_by_id(
            created_holding.id
        )
        assert db_holding is not None
        assert db_holding == created_holding

    @staticmethod
    def test_update_agricultural_holding(
        agricultural_holding_repository: AgriculturalHoldingRepository,
    ) -> None:
        # First, create a holding to update
        holding_candidate = AgriculturalHoldingCandidate(
            owner_user_id="farmer_jane",
            name="Green Acres",
            hatchery="Sunny Hatchery",
            eco_control_number="EC987654",
            breed="Rhode Island Red",
            address_street="456 Country Road",
            address_zip="67890",
            address_city="Countryside",
        )
        created_holding = agricultural_holding_repository.add_holding(holding_candidate)
        holding_id = created_holding.id

        # Now, update the holding
        updated_candidate = AgriculturalHoldingCandidate(
            owner_user_id="farmer_jane_updated",
            name="Green Acres Updated",
            hatchery="Sunny Hatchery Updated",
            eco_control_number="EC987654_UPDATED",
            breed="Rhode Island Red Updated",
            address_street="456 Country Road Updated",
            address_zip="67890_UPDATED",
            address_city="Countryside Updated",
        )
        updated_holding = agricultural_holding_repository.update_holding(
            holding_id, updated_candidate
        )

        assert updated_holding.id == holding_id
        assert updated_holding.owner_user_id == updated_candidate.owner_user_id
        assert updated_holding.name == updated_candidate.name
        assert updated_holding.hatchery == updated_candidate.hatchery
        assert (
            updated_holding.eco_control_number == updated_candidate.eco_control_number
        )
        assert updated_holding.breed == updated_candidate.breed
        assert updated_holding.address_street == updated_candidate.address_street
        assert updated_holding.address_zip == updated_candidate.address_zip
        assert updated_holding.address_city == updated_candidate.address_city

        # Read back from the database to ensure it was updated correctly
        db_holding = agricultural_holding_repository.get_holding_by_id(holding_id)
        assert db_holding is not None
        assert db_holding == updated_holding

    @staticmethod
    def test_reads_all_agricultural_holdings(
        agricultural_holding_repository: AgriculturalHoldingRepository,
    ) -> None:
        # Create multiple holdings
        holding_candidates = [
            AgriculturalHoldingCandidate(
                owner_user_id="farmer_a",
                name="Farm A",
                hatchery="Hatchery A",
                eco_control_number="EC000001",
                breed="Breed A",
                address_street="1 A St",
                address_zip="10001",
                address_city="City A",
            ),
            AgriculturalHoldingCandidate(
                owner_user_id="farmer_b",
                name="Farm B",
                hatchery="Hatchery B",
                eco_control_number="EC000002",
                breed="Breed B",
                address_street="2 B St",
                address_zip="20002",
                address_city="City B",
            ),
            AgriculturalHoldingCandidate(
                owner_user_id="farmer_c",
                name="Farm C",
                hatchery="Hatchery C",
                eco_control_number="EC000003",
                breed="Breed C",
                address_street="3 C St",
                address_zip="30003",
                address_city="City C",
            ),
        ]

        created_holdings = [
            agricultural_holding_repository.add_holding(candidate)
            for candidate in holding_candidates
        ]

        all_holdings = agricultural_holding_repository.all_holdings()

        assert len(all_holdings) >= len(created_holdings)
        for created_holding in created_holdings:
            assert created_holding in all_holdings

    @staticmethod
    def test_get_agricultural_holding_by_id(
        agricultural_holding_repository: AgriculturalHoldingRepository,
    ) -> None:
        holding_candidate = AgriculturalHoldingCandidate(
            owner_user_id="farmer_xyz",
            name="XYZ Farm",
            hatchery="XYZ Hatchery",
            eco_control_number="ECXYZ123",
            breed="Breed XYZ",
            address_street="789 XYZ Blvd",
            address_zip="99999",
            address_city="XYZ City",
        )
        created_holding = agricultural_holding_repository.add_holding(holding_candidate)

        holding_id = created_holding.id
        fetched_holding = agricultural_holding_repository.get_holding_by_id(holding_id)
        assert fetched_holding is not None
        assert fetched_holding == created_holding

    @staticmethod
    def test_get_agricultural_holding_by_id_not_found(
        agricultural_holding_repository: AgriculturalHoldingRepository,
    ) -> None:
        non_existent_id = 999999
        fetched_holding = agricultural_holding_repository.get_holding_by_id(
            non_existent_id
        )
        assert fetched_holding is None

    @staticmethod
    def test_get_agricultural_holding_by_owner_name(
        agricultural_holding_repository: AgriculturalHoldingRepository,
    ) -> None:
        holding_candidate = AgriculturalHoldingCandidate(
            owner_user_id="farmer_abc",
            name="ABC Farm",
            hatchery="ABC Hatchery",
            eco_control_number="ECABC123",
            breed="Breed ABC",
            address_street="123 ABC St",
            address_zip="88888",
            address_city="ABC City",
        )
        created_holding = agricultural_holding_repository.add_holding(holding_candidate)

        fetched_holding = agricultural_holding_repository.get_holding_by_owner(
            created_holding.owner_user_id
        )
        assert fetched_holding is not None
        assert fetched_holding == created_holding

    @staticmethod
    def test_get_agricultural_holding_by_owner_name_not_found(
        agricultural_holding_repository: AgriculturalHoldingRepository,
    ) -> None:
        non_existent_owner = "non_existent_farmer"
        fetched_holding = agricultural_holding_repository.get_holding_by_owner(
            non_existent_owner
        )
        assert fetched_holding is None
