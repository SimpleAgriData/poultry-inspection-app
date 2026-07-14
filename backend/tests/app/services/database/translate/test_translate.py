from app.db import models
from app.services.database import translate


class TestTranslate:
    @staticmethod
    def test_translates_a_database_holding_into_a_domain_holding() -> None:
        db_holding = models.AgriculturalHolding(
            id=1,
            owner_user_id="farmer_john",
            name="Sunny Acres",
            hatchery="Hatchery A",
            eco_control_number="EC12345",
            breed="Some Breed",
            address_street="123 Farm Lane",
            address_zip="12345",
            address_city="Farmville",
        )

        domain_holding = translate.holding_to_domain(db_holding)

        assert domain_holding.id == 1
        assert domain_holding.owner_user_id == "farmer_john"
        assert domain_holding.name == "Sunny Acres"
        assert domain_holding.hatchery == "Hatchery A"
        assert domain_holding.eco_control_number == "EC12345"
        assert domain_holding.breed == "Some Breed"
        assert domain_holding.address_street == "123 Farm Lane"
        assert domain_holding.address_zip == "12345"
        assert domain_holding.address_city == "Farmville"
        assert domain_holding.farms == []

    @staticmethod
    def test_falls_back_to_default_id_when_holding_id_is_none() -> None:
        db_holding = models.AgriculturalHolding(
            id=None,
            owner_user_id="farmer_jane",
            name="Green Fields",
            hatchery="Hatchery B",
            eco_control_number="EC54321",
            breed="Another Breed",
            address_street="456 Country Road",
            address_zip="54321",
            address_city="Countryside",
        )

        domain_holding = translate.holding_to_domain(db_holding)

        assert domain_holding.id == 0  # Default fallback
        assert domain_holding.owner_user_id == "farmer_jane"
        assert domain_holding.name == "Green Fields"
        assert domain_holding.hatchery == "Hatchery B"
        assert domain_holding.eco_control_number == "EC54321"
        assert domain_holding.breed == "Another Breed"
        assert domain_holding.address_street == "456 Country Road"
        assert domain_holding.address_zip == "54321"
        assert domain_holding.address_city == "Countryside"
        assert domain_holding.farms == []

    @staticmethod
    def test_translates_a_database_farm_into_a_domain_farm() -> None:
        db_holding = models.AgriculturalHolding(
            id=2,
            owner_user_id="farmer_fiona",
            name="Blue Meadow",
            hatchery="Hatchery C",
            eco_control_number="EC22222",
            breed="Breed C",
            address_street="22 Field Way",
            address_zip="22222",
            address_city="Bluetown",
        )
        db_farm = models.Farm(
            id=10,
            name="Main Farm",
            type=models.FarmType.FATTENING,
            holding_id=2,
            holding=db_holding,
            vvvo_number="VV22222",
        )

        domain_farm = translate.farm_to_domain(db_farm)

        assert domain_farm.id == 10
        assert domain_farm.name == "Main Farm"
        assert domain_farm.type.value == "fattening"
        assert domain_farm.vvvo_number == "VV22222"
        assert domain_farm.holding.id == 2
        assert domain_farm.sections == []

    @staticmethod
    def test_falls_back_to_default_id_when_farm_id_is_none() -> None:
        db_holding = models.AgriculturalHolding(
            id=3,
            owner_user_id="farmer_frank",
            name="Red River",
            hatchery="Hatchery D",
            eco_control_number="EC33333",
            breed="Breed D",
            address_street="33 River Rd",
            address_zip="33333",
            address_city="Redcity",
        )
        db_farm = models.Farm(
            id=None,
            name="North Farm",
            type=models.FarmType.REARING,
            holding_id=3,
            holding=db_holding,
            vvvo_number="VV33333",
        )

        domain_farm = translate.farm_to_domain(db_farm)

        assert domain_farm.id == 0  # Default fallback
        assert domain_farm.name == "North Farm"
        assert domain_farm.type.value == "rearing"
        assert domain_farm.vvvo_number == "VV33333"
        assert domain_farm.holding.id == 3
        assert domain_farm.sections == []

    @staticmethod
    def test_translates_a_database_section_into_a_domain_section() -> None:
        db_holding = models.AgriculturalHolding(
            id=6,
            owner_user_id="farmer_sam",
            name="Emerald Farm",
            hatchery="Hatchery G",
            eco_control_number="EC66666",
            breed="Breed G",
            address_street="66 Emerald Ave",
            address_zip="66666",
            address_city="Emerald City",
        )
        db_farm = models.Farm(
            id=13,
            name="South Farm",
            type=models.FarmType.FATTENING,
            holding_id=6,
            holding=db_holding,
            vvvo_number="VV66666",
        )
        db_section = models.Section(
            id=30,
            name="Section 1",
            farm_id=13,
            farm=db_farm,
        )

        domain_section = translate.section_to_domain(db_section)

        assert domain_section.id == 30
        assert domain_section.name == "Section 1"
        assert domain_section.farm.id == 13
        assert domain_section.farm.vvvo_number == "VV66666"

    @staticmethod
    def test_falls_back_to_default_id_when_section_id_is_none() -> None:
        db_holding = models.AgriculturalHolding(
            id=7,
            owner_user_id="farmer_sue",
            name="Crystal Plains",
            hatchery="Hatchery H",
            eco_control_number="EC77777",
            breed="Breed H",
            address_street="77 Crystal Dr",
            address_zip="77777",
            address_city="Crystal City",
        )
        db_farm = models.Farm(
            id=14,
            name="Northeast Farm",
            type=models.FarmType.REARING,
            holding_id=7,
            holding=db_holding,
            vvvo_number="VV77777",
        )
        db_section = models.Section(
            id=None,
            name="Section 2",
            farm_id=14,
            farm=db_farm,
        )

        domain_section = translate.section_to_domain(db_section)

        assert domain_section.id == 0  # Default fallback
        assert domain_section.name == "Section 2"
        assert domain_section.farm.id == 14
        assert domain_section.farm.vvvo_number == "VV77777"

    @staticmethod
    def test_translates_holding_with_nested_farm() -> None:
        db_holding = models.AgriculturalHolding(
            id=100,
            owner_user_id="owner_nested",
            name="Nested Holding",
            hatchery="H",
            eco_control_number="ECN1",
            breed="R1",
            address_street="1 Nest St",
            address_zip="10000",
            address_city="Nestcity",
        )
        db_farm = models.Farm(
            id=101,
            name="Nested Farm",
            type=models.FarmType.FATTENING,
            holding_id=100,
            holding=db_holding,
            vvvo_number="VVN1",
        )
        db_holding.farms = [db_farm]

        domain_holding = translate.holding_to_domain(db_holding)

        assert domain_holding.id == 100
        assert len(domain_holding.farms) == 1
        domain_farm = domain_holding.farms[0]
        assert domain_farm.id == 101
        assert domain_farm.name == "Nested Farm"
        assert domain_farm.type.value == "fattening"
        assert domain_farm.vvvo_number == "VVN1"
        assert domain_farm.holding is domain_holding

    @staticmethod
    def test_translates_holding_with_nested_farm_and_section() -> None:
        db_holding = models.AgriculturalHolding(
            id=120,
            owner_user_id="owner3",
            name="Holding 3",
            hatchery="H3",
            eco_control_number="ECN3",
            breed="R3",
            address_street="3 Nest St",
            address_zip="12000",
            address_city="Nestburg",
        )
        db_farm = models.Farm(
            id=121,
            name="Farm 3",
            type=models.FarmType.FATTENING,
            holding_id=120,
            holding=db_holding,
            vvvo_number="VVN3",
        )
        db_section = models.Section(
            id=123,
            name="Section 3A-1",
            farm_id=121,
            farm=db_farm,
        )
        db_farm.sections = [db_section]
        db_holding.farms = [db_farm]

        domain_holding = translate.holding_to_domain(db_holding)

        assert domain_holding.id == 120

        assert len(domain_holding.farms) == 1
        domain_farm = domain_holding.farms[0]
        assert domain_farm.id == 121
        assert domain_farm.vvvo_number == "VVN3"
        assert domain_farm.holding is domain_holding

        assert len(domain_farm.sections) == 1
        domain_section = domain_farm.sections[0]
        assert domain_section.id == 123
        assert domain_section.name == "Section 3A-1"
        assert domain_section.farm is domain_farm

    @staticmethod
    def test_translates_farm_with_nested_section() -> None:
        db_holding = models.AgriculturalHolding(
            id=150,
            owner_user_id="owner6",
            name="Holding 6",
            hatchery="H6",
            eco_control_number="ECN6",
            breed="R6",
            address_street="6 Nest St",
            address_zip="15000",
            address_city="Nestburgh",
        )
        db_farm = models.Farm(
            id=151,
            name="Farm 6",
            type=models.FarmType.REARING,
            holding_id=150,
            holding=db_holding,
            vvvo_number="VVN6",
        )
        db_section = models.Section(
            id=153,
            name="Section 6A-1",
            farm_id=151,
            farm=db_farm,
        )
        db_farm.sections = [db_section]

        domain_farm = translate.farm_to_domain(db_farm)

        assert domain_farm.id == 151
        assert domain_farm.vvvo_number == "VVN6"
        assert len(domain_farm.sections) == 1

        domain_section = domain_farm.sections[0]
        assert domain_section.id == 153
        assert domain_section.name == "Section 6A-1"
        assert domain_section.farm is domain_farm
