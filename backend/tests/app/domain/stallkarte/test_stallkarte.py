import datetime

import pytest

from app import domain
from app.domain.stallkarte import events as stallkarte_events
from app.domain.stallkarte.events.models import (
    NoteEntry,
    NoteType,
    WeatherCondition,
)
from app.domain.stallkarte.events.dailyevents.mortality_recorded import (
    MortalityRecordedShift,
)


class TestStartStallkarte:
    @staticmethod
    def test_starts_stallkarte(stallkarte: domain.Stallkarte) -> None:
        today = datetime.date.today()

        events = stallkarte.start_stallkarte(
            date_started=today,
            date_hatched=today,
            hatchery_name="Happy Hatchery",
            breed="Broiler",
            fattening_cycle="Fattening Cycle 1",
            eco_control_number="ECO123456",
            is_eu_bio=True,
            is_naturland=False,
        )

        assert len(events) == 1
        event = events[0]

        assert event.type == stallkarte_events.StallkarteStarted.type()
        data = event.data

        assert isinstance(data, stallkarte_events.StallkarteStarted)
        assert data.date_started == today
        assert data.date_hatched == today
        assert data.hatchery_name == "Happy Hatchery"
        assert data.breed == "Broiler"
        assert data.fattening_cycle == "Fattening Cycle 1"
        assert data.eco_control_number == "ECO123456"
        assert data.is_eu_bio is True
        assert data.is_naturland is False

    @staticmethod
    def test_fails_if_stallkarte_already_started(
        aggregator: domain.StallkarteAggregator,
    ) -> None:
        today = datetime.date.today()
        stallkarte = aggregator.stallkarte

        # Start the stallkarte for the first time
        events = stallkarte.start_stallkarte(
            date_started=today,
            date_hatched=today,
            hatchery_name="Happy Hatchery",
            breed="Broiler",
            fattening_cycle="Fattening Cycle 1",
            eco_control_number="ECO123456",
            is_eu_bio=True,
            is_naturland=False,
        )
        aggregator.apply_all(events)

        with pytest.raises(domain.Exception) as exc_info:
            # Attempt to start the stallkarte again
            stallkarte.start_stallkarte(
                date_started=today,
                date_hatched=today,
                hatchery_name="Happy Hatchery",
                breed="Broiler",
                fattening_cycle="Fattening Cycle 1",
                eco_control_number="ECO123456",
                is_eu_bio=True,
                is_naturland=False,
            )

        e = exc_info.value
        assert e.message == "stallkarte has already been started"


class TestReviseDetails:
    @staticmethod
    def test_revises_details(started_aggregator: domain.StallkarteAggregator) -> None:
        stallkarte = started_aggregator.stallkarte
        today = datetime.date.today()

        revised_events = stallkarte.revise_details(
            date_hatched=today - datetime.timedelta(days=1),
            hatchery_name="Better Hatchery",
            breed="Layer",
            fattening_cycle="Fattening Cycle 2",
            is_eu_bio=False,
            is_naturland=True,
        )

        assert len(revised_events) == 1
        event = revised_events[0]

        assert event.type == stallkarte_events.DetailsRevised.type()
        data = event.data

        assert isinstance(data, stallkarte_events.DetailsRevised)
        assert data.date_hatched == today - datetime.timedelta(days=1)
        assert data.hatchery_name == "Better Hatchery"
        assert data.breed == "Layer"
        assert data.fattening_cycle == "Fattening Cycle 2"
        assert data.is_eu_bio is False
        assert data.is_naturland is True

    @staticmethod
    def test_fails_if_stallkarte_not_started(stallkarte: domain.Stallkarte) -> None:
        today = datetime.date.today()

        with pytest.raises(domain.Exception) as exc_info:
            stallkarte.revise_details(
                date_hatched=today - datetime.timedelta(days=1),
                hatchery_name="Better Hatchery",
                breed="Layer",
                fattening_cycle="Fattening Cycle 2",
                is_eu_bio=False,
                is_naturland=True,
            )

        e = exc_info.value
        assert e.message == "stallkarte has not been started yet"


class TestAssignRearingFarm:
    @staticmethod
    def test_assigns_rearing_farm(
        started_aggregator: domain.StallkarteAggregator,
        holding: domain.AgriculturalHolding,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        farm = domain.Farm(
            holding=holding,
            id=1,
            vvvo_number="VV100000",
            name="Rearing Farm 1",
            type=domain.FarmType.REARING,
            sections=[],
        )
        farm.sections = [
            domain.Section(
                id=1,
                name="Section 1",
                farm=farm,
            ),
            domain.Section(
                id=2,
                name="Section 2",
                farm=farm,
            ),
        ]

        events = stallkarte.assign_rearing_farm(farm=farm)

        assert len(events) == 1
        event = events[0]

        assert event.type == stallkarte_events.RearingFarmAssigned.type()
        data = event.data

        assert isinstance(data, stallkarte_events.RearingFarmAssigned)
        assert data.farm_id == farm.id
        assert data.farm_name == farm.name
        assert data.farm_vvvo_number == farm.vvvo_number
        assert data.farm_type == farm.type
        assert len(data.sections) == 2

        section1 = data.sections[0]
        assert section1.id == farm.sections[0].id
        assert section1.name == farm.sections[0].name
        assert section1.number == 1

        section2 = data.sections[1]
        assert section2.id == farm.sections[1].id
        assert section2.name == farm.sections[1].name
        assert section2.number == 2

    @staticmethod
    def test_assigns_combined_farm(
        started_aggregator: domain.StallkarteAggregator,
        holding: domain.AgriculturalHolding,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        farm = domain.Farm(
            holding=holding,
            id=1,
            vvvo_number="VV100000",
            name="Combined Farm 1",
            type=domain.FarmType.COMBINED,
            sections=[],
        )
        farm.sections = [
            domain.Section(
                id=1,
                name="Section 1",
                farm=farm,
            ),
            domain.Section(
                id=2,
                name="Section 2",
                farm=farm,
            ),
        ]

        events = stallkarte.assign_rearing_farm(farm=farm)

        assert len(events) == 1
        event = events[0]

        assert event.type == stallkarte_events.RearingFarmAssigned.type()
        data = event.data

        assert isinstance(data, stallkarte_events.RearingFarmAssigned)
        assert data.farm_id == farm.id
        assert data.farm_name == farm.name
        assert data.farm_vvvo_number == farm.vvvo_number
        assert data.farm_type == farm.type
        assert len(data.sections) == 2

        section1 = data.sections[0]
        assert section1.id == farm.sections[0].id
        assert section1.name == farm.sections[0].name
        assert section1.number == 1

        section2 = data.sections[1]
        assert section2.id == farm.sections[1].id
        assert section2.name == farm.sections[1].name
        assert section2.number == 2

    @staticmethod
    def test_fails_if_farm_is_not_rearing_farm(
        started_aggregator: domain.StallkarteAggregator,
        holding: domain.AgriculturalHolding,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        farm = domain.Farm(
            holding=holding,
            id=1,
            vvvo_number="VV100000",
            name="Fattening Farm 1",
            type=domain.FarmType.FATTENING,
            sections=[],
        )

        with pytest.raises(domain.Exception) as exc_info:
            stallkarte.assign_rearing_farm(farm=farm)

        e = exc_info.value
        assert e.message == "assigned farm is not a rearing or combined farm"

    @staticmethod
    def test_fails_if_number_of_sections_differ_from_fattening_farm(
        started_aggregator: domain.StallkarteAggregator,
        holding: domain.AgriculturalHolding,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        fattening_farm = domain.Farm(
            holding=holding,
            id=1,
            vvvo_number="VV100000",
            name="Rearing Farm 1",
            type=domain.FarmType.FATTENING,
            sections=[],
        )
        fattening_farm.sections = [
            domain.Section(
                id=1,
                name="Section 1",
                farm=fattening_farm,
            ),
        ]

        events = stallkarte.assign_fattening_farm(farm=fattening_farm)
        started_aggregator.apply_all(events)

        rearing_farm = domain.Farm(
            holding=holding,
            id=2,
            vvvo_number="VV100001",
            name="Rearing Farm 1",
            type=domain.FarmType.REARING,
            sections=[],
        )
        rearing_farm.sections = [
            domain.Section(
                id=1,
                name="Section 1",
                farm=rearing_farm,
            ),
            domain.Section(
                id=2,
                name="Section 2",
                farm=rearing_farm,
            ),
        ]

        with pytest.raises(domain.Exception) as exc_info:
            stallkarte.assign_rearing_farm(farm=rearing_farm)

        e = exc_info.value
        assert (
            e.message == "rearing farm must have the same number of sections as "
            "the fattening farm"
        )

    @staticmethod
    def test_fails_if_a_production_day_has_already_been_recorded(
        started_aggregator: domain.StallkarteAggregator,
        holding: domain.AgriculturalHolding,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        farm = domain.Farm(
            holding=holding,
            id=1,
            vvvo_number="VV100000",
            name="Combined Farm 1",
            type=domain.FarmType.COMBINED,
            sections=[],
        )
        farm.sections = [
            domain.Section(
                id=1,
                name="Section 1",
                farm=farm,
            ),
            domain.Section(
                id=2,
                name="Section 2",
                farm=farm,
            ),
        ]

        events = stallkarte.assign_rearing_farm(farm=farm)
        started_aggregator.apply_all(events)

        production_day_events = stallkarte.record_weight(
            production_day=1,
            weight_grams=1000,
        )
        started_aggregator.apply_all(production_day_events)

        with pytest.raises(domain.Exception) as exc_info:
            stallkarte.assign_rearing_farm(farm=farm)

        e = exc_info.value
        assert (
            e.message
            == "cannot change rearing farm after the first production day has "
            "been recorded"
        )


class TestAssignFatteningFarm:
    @staticmethod
    def test_assigns_fattening_farm(
        started_aggregator: domain.StallkarteAggregator,
        holding: domain.AgriculturalHolding,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        farm = domain.Farm(
            holding=holding,
            id=1,
            vvvo_number="VV100000",
            name="Fattening Farm 1",
            type=domain.FarmType.FATTENING,
            sections=[],
        )
        farm.sections = [
            domain.Section(
                id=1,
                name="Section 1",
                farm=farm,
            ),
            domain.Section(
                id=2,
                name="Section 2",
                farm=farm,
            ),
        ]

        events = stallkarte.assign_fattening_farm(farm=farm)

        assert len(events) == 1
        event = events[0]

        assert event.type == stallkarte_events.FatteningFarmAssigned.type()
        data = event.data

        assert isinstance(data, stallkarte_events.FatteningFarmAssigned)
        assert data.farm_id == farm.id
        assert data.farm_name == farm.name
        assert data.farm_vvvo_number == farm.vvvo_number
        assert data.farm_type == farm.type
        assert len(data.sections) == 2

        section1 = data.sections[0]
        assert section1.id == farm.sections[0].id
        assert section1.name == farm.sections[0].name
        assert section1.number == 1

        section2 = data.sections[1]
        assert section2.id == farm.sections[1].id
        assert section2.name == farm.sections[1].name
        assert section2.number == 2

    @staticmethod
    def test_assigns_combined_farm_as_fattening_farm(
        started_aggregator: domain.StallkarteAggregator,
        holding: domain.AgriculturalHolding,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        farm = domain.Farm(
            holding=holding,
            id=1,
            vvvo_number="VV100000",
            name="Combined Farm 1",
            type=domain.FarmType.COMBINED,
            sections=[],
        )
        farm.sections = [
            domain.Section(
                id=1,
                name="Section 1",
                farm=farm,
            ),
            domain.Section(
                id=2,
                name="Section 2",
                farm=farm,
            ),
        ]

        events = stallkarte.assign_fattening_farm(farm=farm)

        assert len(events) == 1
        event = events[0]

        assert event.type == stallkarte_events.FatteningFarmAssigned.type()
        data = event.data

        assert isinstance(data, stallkarte_events.FatteningFarmAssigned)
        assert data.farm_id == farm.id
        assert data.farm_name == farm.name
        assert data.farm_vvvo_number == farm.vvvo_number
        assert data.farm_type == farm.type
        assert len(data.sections) == 2

        section1 = data.sections[0]
        assert section1.id == farm.sections[0].id
        assert section1.name == farm.sections[0].name
        assert section1.number == 1

        section2 = data.sections[1]
        assert section2.id == farm.sections[1].id
        assert section2.name == farm.sections[1].name
        assert section2.number == 2

    @staticmethod
    def test_fails_if_farm_is_not_fattening_farm(
        started_aggregator: domain.StallkarteAggregator,
        holding: domain.AgriculturalHolding,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        farm = domain.Farm(
            holding=holding,
            id=1,
            vvvo_number="VV100000",
            name="Rearing Farm 1",
            type=domain.FarmType.REARING,
            sections=[],
        )

        with pytest.raises(domain.Exception) as exc_info:
            stallkarte.assign_fattening_farm(farm=farm)

        e = exc_info.value
        assert e.message == "assigned farm is not a fattening or combined farm"

    @staticmethod
    def test_fails_if_number_of_sections_differ_from_rearing_farm(
        started_aggregator: domain.StallkarteAggregator,
        holding: domain.AgriculturalHolding,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        rearing_farm = domain.Farm(
            holding=holding,
            id=1,
            vvvo_number="VV100000",
            name="Rearing Farm 1",
            type=domain.FarmType.REARING,
            sections=[],
        )
        rearing_farm.sections = [
            domain.Section(
                id=1,
                name="Section 1",
                farm=rearing_farm,
            ),
            domain.Section(
                id=2,
                name="Section 2",
                farm=rearing_farm,
            ),
        ]

        events = stallkarte.assign_rearing_farm(farm=rearing_farm)
        started_aggregator.apply_all(events)

        fattening_farm = domain.Farm(
            holding=holding,
            id=2,
            vvvo_number="VV100001",
            name="Fattening Farm 1",
            type=domain.FarmType.FATTENING,
            sections=[],
        )
        fattening_farm.sections = [
            domain.Section(
                id=1,
                name="Section 1",
                farm=fattening_farm,
            ),
        ]

        with pytest.raises(domain.Exception) as exc_info:
            stallkarte.assign_fattening_farm(farm=fattening_farm)

        e = exc_info.value
        assert (
            e.message == "fattening farm must have the same number of sections as "
            "the rearing farm"
        )


class TestTransferFlock:
    @staticmethod
    def test_transfers_flock(
        started_aggregator: domain.StallkarteAggregator,
        holding: domain.AgriculturalHolding,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        from_farm = domain.Farm(
            holding=holding,
            id=1,
            vvvo_number="VV100000",
            name="From Farm",
            type=domain.FarmType.COMBINED,
            sections=[],
        )
        from_farm.sections = [
            domain.Section(
                id=1,
                name="Section 1",
                farm=from_farm,
            ),
            domain.Section(
                id=2,
                name="Section 2",
                farm=from_farm,
            ),
        ]

        to_farm = domain.Farm(
            holding=holding,
            id=2,
            vvvo_number="VV100001",
            name="To Farm",
            type=domain.FarmType.COMBINED,
            sections=[],
        )
        to_farm.sections = [
            domain.Section(
                id=3,
                name="Section 3",
                farm=to_farm,
            ),
            domain.Section(
                id=4,
                name="Section 4",
                farm=to_farm,
            ),
        ]

        events = stallkarte.assign_rearing_farm(farm=from_farm)
        started_aggregator.apply_all(events)

        events = stallkarte.assign_fattening_farm(farm=from_farm)
        started_aggregator.apply_all(events)

        today = datetime.date.today()
        transfer_events = stallkarte.transfer_flock(
            transfer_date=today,
            animals_by_section_number={
                1: 2000,
                2: 3000,
            },
        )

        assert len(transfer_events) == 1
        event = transfer_events[0]

        assert event.type == stallkarte_events.FlockTransferred.type()
        assert isinstance(event.data, stallkarte_events.FlockTransferred)
        data = event.data

        assert data.transfer_date == today
        assert len(data.animals_by_section) == 2
        assert data.animals_by_section[1] == 2000
        assert data.animals_by_section[2] == 3000

    @staticmethod
    def test_fails_if_flock_already_transferred(
        started_aggregator: domain.StallkarteAggregator,
        holding: domain.AgriculturalHolding,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        from_farm = domain.Farm(
            holding=holding,
            id=1,
            vvvo_number="VV100000",
            name="From Farm",
            type=domain.FarmType.COMBINED,
            sections=[],
        )
        from_farm.sections = [
            domain.Section(
                id=1,
                name="Section 1",
                farm=from_farm,
            ),
            domain.Section(
                id=2,
                name="Section 2",
                farm=from_farm,
            ),
        ]

        events = stallkarte.assign_rearing_farm(farm=from_farm)
        started_aggregator.apply_all(events)

        events = stallkarte.assign_fattening_farm(farm=from_farm)
        started_aggregator.apply_all(events)

        today = datetime.date.today()
        transfer_events = stallkarte.transfer_flock(
            transfer_date=today,
            animals_by_section_number={
                1: 2000,
                2: 3000,
            },
        )
        started_aggregator.apply_all(transfer_events)

        with pytest.raises(domain.Exception) as exc_info:
            stallkarte.transfer_flock(
                transfer_date=today + datetime.timedelta(days=1),
                animals_by_section_number={
                    1: 2000,
                    2: 3000,
                },
            )

        e = exc_info.value
        assert e.message == "flock has already been transferred"

    @staticmethod
    def test_fails_if_fattening_farm_not_assigned(
        started_aggregator: domain.StallkarteAggregator,
        holding: domain.AgriculturalHolding,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        from_farm = domain.Farm(
            holding=holding,
            id=1,
            vvvo_number="VV100000",
            name="From Farm",
            type=domain.FarmType.COMBINED,
            sections=[],
        )
        from_farm.sections = [
            domain.Section(
                id=1,
                name="Section 1",
                farm=from_farm,
            ),
            domain.Section(
                id=2,
                name="Section 2",
                farm=from_farm,
            ),
        ]

        events = stallkarte.assign_rearing_farm(farm=from_farm)
        started_aggregator.apply_all(events)

        today = datetime.date.today()
        with pytest.raises(domain.Exception) as exc_info:
            stallkarte.transfer_flock(
                transfer_date=today,
                animals_by_section_number={
                    1: 2000,
                    2: 3000,
                },
            )

        e = exc_info.value
        assert e.message == "fattening farm is not assigned"

    @staticmethod
    def test_fails_if_number_of_animals_for_a_section_is_not_provided(
        started_aggregator: domain.StallkarteAggregator,
        holding: domain.AgriculturalHolding,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        from_farm = domain.Farm(
            holding=holding,
            id=1,
            vvvo_number="VV100000",
            name="From Farm",
            type=domain.FarmType.COMBINED,
            sections=[],
        )
        from_farm.sections = [
            domain.Section(
                id=1,
                name="Section 1",
                farm=from_farm,
            ),
            domain.Section(
                id=2,
                name="Section 2",
                farm=from_farm,
            ),
        ]

        events = stallkarte.assign_rearing_farm(farm=from_farm)
        started_aggregator.apply_all(events)

        events = stallkarte.assign_fattening_farm(farm=from_farm)
        started_aggregator.apply_all(events)

        today = datetime.date.today()
        with pytest.raises(domain.Exception) as exc_info:
            stallkarte.transfer_flock(
                transfer_date=today,
                animals_by_section_number={
                    1: 2000,
                    # missing section 2
                },
            )

        e = exc_info.value
        assert e.message == "number of animals for section 2 not provided"

    @staticmethod
    def test_fails_if_number_of_animals_for_a_section_is_less_than_zero(
        started_aggregator: domain.StallkarteAggregator,
        holding: domain.AgriculturalHolding,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        from_farm = domain.Farm(
            holding=holding,
            id=1,
            vvvo_number="VV100000",
            name="From Farm",
            type=domain.FarmType.COMBINED,
            sections=[],
        )
        from_farm.sections = [
            domain.Section(
                id=1,
                name="Section 1",
                farm=from_farm,
            ),
            domain.Section(
                id=2,
                name="Section 2",
                farm=from_farm,
            ),
        ]

        events = stallkarte.assign_rearing_farm(farm=from_farm)
        started_aggregator.apply_all(events)

        events = stallkarte.assign_fattening_farm(farm=from_farm)
        started_aggregator.apply_all(events)

        today = datetime.date.today()
        with pytest.raises(domain.Exception) as exc_info:
            stallkarte.transfer_flock(
                transfer_date=today,
                animals_by_section_number={
                    1: 2000,
                    2: -1,  # invalid number of animals
                },
            )

        e = exc_info.value
        assert e.message == "number of animals for section 2 must be non-negative"


class TestReviseTransferDetails:
    @staticmethod
    def test_revises_transfer_details(
        started_aggregator: domain.StallkarteAggregator,
        holding: domain.AgriculturalHolding,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        from_farm = domain.Farm(
            holding=holding,
            id=1,
            vvvo_number="VV100000",
            name="From Farm",
            type=domain.FarmType.COMBINED,
            sections=[],
        )
        from_farm.sections = [
            domain.Section(
                id=1,
                name="Section 1",
                farm=from_farm,
            ),
            domain.Section(
                id=2,
                name="Section 2",
                farm=from_farm,
            ),
        ]

        to_farm = domain.Farm(
            holding=holding,
            id=2,
            vvvo_number="VV100001",
            name="To Farm",
            type=domain.FarmType.COMBINED,
            sections=[],
        )
        to_farm.sections = [
            domain.Section(
                id=3,
                name="Section 3",
                farm=to_farm,
            ),
            domain.Section(
                id=4,
                name="Section 4",
                farm=to_farm,
            ),
        ]

        events = stallkarte.assign_rearing_farm(farm=from_farm)
        started_aggregator.apply_all(events)

        events = stallkarte.assign_fattening_farm(farm=from_farm)
        started_aggregator.apply_all(events)

        today = datetime.date.today()
        transfer_events = stallkarte.transfer_flock(
            transfer_date=today,
            animals_by_section_number={
                1: 2000,
                2: 3000,
            },
        )
        started_aggregator.apply_all(transfer_events)

        revised_transfer_events = stallkarte.revise_transfer_details(
            animals_by_section_number={
                1: 2500,  # updated number of animals for section 1
                2: 3000,  # unchanged number of animals for section 2
            },
        )

        assert len(revised_transfer_events) == 1
        event = revised_transfer_events[0]

        assert event.type == stallkarte_events.TransferDetailsRevised.type()
        assert isinstance(event.data, stallkarte_events.TransferDetailsRevised)
        data = event.data

        assert len(data.animals_by_section) == 2
        assert data.animals_by_section[1] == 2500
        assert data.animals_by_section[2] == 3000

    @staticmethod
    def test_fails_if_flock_has_not_been_transferred_yet(
        started_aggregator: domain.StallkarteAggregator,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        with pytest.raises(domain.Exception) as exc_info:
            stallkarte.revise_transfer_details(
                animals_by_section_number={
                    1: 2500,
                    2: 3000,
                },
            )

        e = exc_info.value
        assert e.message == "flock has not been transferred yet"

    @staticmethod
    def test_fails_if_number_of_animals_for_a_section_is_not_provided(
        started_aggregator: domain.StallkarteAggregator,
        holding: domain.AgriculturalHolding,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        from_farm = domain.Farm(
            holding=holding,
            id=1,
            vvvo_number="VV100000",
            name="From Farm",
            type=domain.FarmType.COMBINED,
            sections=[],
        )
        from_farm.sections = [
            domain.Section(
                id=1,
                name="Section 1",
                farm=from_farm,
            ),
            domain.Section(
                id=2,
                name="Section 2",
                farm=from_farm,
            ),
        ]

        events = stallkarte.assign_rearing_farm(farm=from_farm)
        started_aggregator.apply_all(events)

        events = stallkarte.assign_fattening_farm(farm=from_farm)
        started_aggregator.apply_all(events)

        today = datetime.date.today()
        transfer_events = stallkarte.transfer_flock(
            transfer_date=today,
            animals_by_section_number={
                1: 2000,
                2: 3000,
            },
        )
        started_aggregator.apply_all(transfer_events)

        with pytest.raises(domain.Exception) as exc_info:
            stallkarte.revise_transfer_details(
                animals_by_section_number={
                    1: 2500,
                    # missing section 2
                },
            )

        e = exc_info.value
        assert e.message == "number of animals for section 2 not provided"

    @staticmethod
    def test_fails_if_number_of_animals_for_a_section_is_less_than_zero(
        started_aggregator: domain.StallkarteAggregator,
        holding: domain.AgriculturalHolding,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        from_farm = domain.Farm(
            holding=holding,
            id=1,
            vvvo_number="VV100000",
            name="From Farm",
            type=domain.FarmType.COMBINED,
            sections=[],
        )
        from_farm.sections = [
            domain.Section(
                id=1,
                name="Section 1",
                farm=from_farm,
            ),
            domain.Section(
                id=2,
                name="Section 2",
                farm=from_farm,
            ),
        ]

        events = stallkarte.assign_rearing_farm(farm=from_farm)
        started_aggregator.apply_all(events)

        events = stallkarte.assign_fattening_farm(farm=from_farm)
        started_aggregator.apply_all(events)

        today = datetime.date.today()
        transfer_events = stallkarte.transfer_flock(
            transfer_date=today,
            animals_by_section_number={
                1: 2000,
                2: 3000,
            },
        )
        started_aggregator.apply_all(transfer_events)

        with pytest.raises(domain.Exception) as exc_info:
            stallkarte.revise_transfer_details(
                animals_by_section_number={
                    1: 2500,
                    2: -1,  # invalid number of animals
                },
            )

        e = exc_info.value
        assert e.message == "number of animals for section 2 must be non-negative"


class TestRecordAmbientClimate:
    @staticmethod
    def test_records_ambient_climate(
        started_aggregator: domain.StallkarteAggregator,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        events = stallkarte.record_ambient_climate(
            production_day=0,
            temperature_celsius=25.5,
            humidity_percent=60.0,
        )

        assert len(events) == 1
        event = events[0]

        assert event.type == stallkarte_events.AmbientClimateRecorded.type()
        assert isinstance(event.data, stallkarte_events.AmbientClimateRecorded)
        data = event.data

        assert data.production_day == 0
        assert data.temperature_celsius == 25.5
        assert data.humidity_percent == 60.0

    @staticmethod
    def test_fails_if_production_day_is_negative(
        started_aggregator: domain.StallkarteAggregator,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        with pytest.raises(domain.Exception) as exc_info:
            stallkarte.record_ambient_climate(
                production_day=-1,
                temperature_celsius=25.5,
                humidity_percent=60.0,
            )

        e = exc_info.value
        assert e.message == "production_day must be non-negative"


class TestRecordFeedConsumption:
    @staticmethod
    def test_records_feed_consumption(
        started_aggregator: domain.StallkarteAggregator,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        events = stallkarte.record_feed_consumption(
            production_day=0,
            amount_kg=100.0,
        )

        assert len(events) == 1
        event = events[0]

        assert event.type == stallkarte_events.FeedConsumptionRecorded.type()
        assert isinstance(event.data, stallkarte_events.FeedConsumptionRecorded)
        data = event.data

        assert data.production_day == 0
        assert data.amount_kg == 100.0

    @staticmethod
    def test_fails_if_production_day_is_negative(
        started_aggregator: domain.StallkarteAggregator,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        with pytest.raises(domain.Exception) as exc_info:
            stallkarte.record_feed_consumption(
                production_day=-1,
                amount_kg=100.0,
            )

        e = exc_info.value
        assert e.message == "production_day must be non-negative"


class TestRecordFatteningDayData:
    @staticmethod
    def test_records_fattening_day_data(
        started_aggregator: domain.StallkarteAggregator,
    ) -> None:
        stallkarte = started_aggregator.stallkarte
        stallkarte.state.transfer = domain.StallkarteTransfer(
            date=datetime.date.today(),
            production_day=12,
            animals_by_section_number={1: 2000},
        )

        events = stallkarte.record_fattening_day_data(
            production_day=12,
            opening_time="09:00",
            weather_conditions=[WeatherCondition.SUN, WeatherCondition.STRONG_WIND],
            veterinarian=True,
        )

        assert len(events) == 1
        event = events[0]

        assert event.type == stallkarte_events.FatteningDayDataRecorded.type()
        assert isinstance(event.data, stallkarte_events.FatteningDayDataRecorded)
        data = event.data

        assert data.production_day == 12
        assert data.opening_time == "09:00"
        assert data.weather_conditions == [
            WeatherCondition.SUN,
            WeatherCondition.STRONG_WIND,
        ]
        assert data.veterinarian is True

    @staticmethod
    def test_fails_before_transfer(
        started_aggregator: domain.StallkarteAggregator,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        with pytest.raises(domain.Exception) as exc_info:
            stallkarte.record_fattening_day_data(
                production_day=0,
                opening_time="09:00",
                weather_conditions=[WeatherCondition.SUN],
                veterinarian=False,
            )

        e = exc_info.value
        assert e.message == "fattening day data can only be recorded after transfer"

    @staticmethod
    def test_fails_if_production_day_is_negative(
        started_aggregator: domain.StallkarteAggregator,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        with pytest.raises(domain.Exception) as exc_info:
            stallkarte.record_fattening_day_data(
                production_day=-1,
                opening_time=None,
                weather_conditions=[],
                veterinarian=False,
            )

        e = exc_info.value
        assert e.message == "production_day must be non-negative"


class TestRecordWaterConsumption:
    @staticmethod
    def test_records_water_consumption(
        started_aggregator: domain.StallkarteAggregator,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        events = stallkarte.record_water_consumption(
            production_day=0,
            amount_liters=200.0,
        )

        assert len(events) == 1
        event = events[0]

        assert event.type == stallkarte_events.WaterConsumptionRecorded.type()
        assert isinstance(event.data, stallkarte_events.WaterConsumptionRecorded)
        data = event.data

        assert data.production_day == 0
        assert data.amount_liters == 200.0

    @staticmethod
    def test_fails_if_production_day_is_negative(
        started_aggregator: domain.StallkarteAggregator,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        with pytest.raises(domain.Exception) as exc_info:
            stallkarte.record_water_consumption(
                production_day=-1,
                amount_liters=200.0,
            )

        e = exc_info.value
        assert e.message == "production_day must be non-negative"


class TestRecordWeight:
    @staticmethod
    def test_records_weight(
        started_aggregator: domain.StallkarteAggregator,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        events = stallkarte.record_weight(
            production_day=0,
            weight_grams=1500.0,
        )

        assert len(events) == 1
        event = events[0]

        assert event.type == stallkarte_events.WeightRecorded.type()
        assert isinstance(event.data, stallkarte_events.WeightRecorded)
        data = event.data

        assert data.production_day == 0
        assert data.weight_grams == 1500.0

    @staticmethod
    def test_fails_if_production_day_is_negative(
        started_aggregator: domain.StallkarteAggregator,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        with pytest.raises(domain.Exception) as exc_info:
            stallkarte.record_weight(
                production_day=-1,
                weight_grams=1500.0,
            )

        e = exc_info.value
        assert e.message == "production_day must be non-negative"


class TestSaveGeneralNotes:
    @staticmethod
    def test_saves_general_notes(
        started_aggregator: domain.StallkarteAggregator,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        events = stallkarte.save_general_notes(
            production_day=0,
            general_notes=[
                NoteEntry(
                    id="note-1",
                    note_type=NoteType.OTHER,
                    note_text="This is a general note.",
                )
            ],
        )

        assert len(events) == 1
        event = events[0]

        assert event.type == stallkarte_events.GeneralNotesReplaced.type()
        assert isinstance(event.data, stallkarte_events.GeneralNotesReplaced)
        data = event.data

        assert data.production_day == 0
        assert len(data.general_notes) == 1
        assert data.general_notes[0].id == "note-1"
        assert data.general_notes[0].note_type == NoteType.OTHER
        assert data.general_notes[0].note_text == "This is a general note."

    @staticmethod
    def test_fails_if_production_day_is_negative(
        started_aggregator: domain.StallkarteAggregator,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        with pytest.raises(domain.Exception) as exc_info:
            stallkarte.save_general_notes(
                production_day=-1,
                general_notes=[],
            )

        e = exc_info.value
        assert e.message == "production_day must be non-negative"


class TestSaveFinishNotes:
    @staticmethod
    def test_saves_finish_notes(
        started_aggregator: domain.StallkarteAggregator,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        events = stallkarte.save_finish_notes(
            finish_notes=[
                NoteEntry(
                    id="finish-note-1",
                    note_type=NoteType.SLAUGHTER,
                    slaughter_animals_count=1200,
                )
            ],
        )

        assert len(events) == 1
        event = events[0]

        assert event.type == stallkarte_events.FinishNotesReplaced.type()
        assert isinstance(event.data, stallkarte_events.FinishNotesReplaced)
        data = event.data

        assert len(data.finish_notes) == 1
        assert data.finish_notes[0].id == "finish-note-1"
        assert data.finish_notes[0].slaughter_animals_count == 1200


class TestRecordMortality:
    @staticmethod
    def test_records_mortality_during_rearing(
        started_aggregator: domain.StallkarteAggregator,
        holding: domain.AgriculturalHolding,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        farm = domain.Farm(
            holding=holding,
            id=1,
            vvvo_number="VV100000",
            name="Rearing Farm 1",
            type=domain.FarmType.REARING,
            sections=[],
        )
        farm.sections = [
            domain.Section(
                id=1,
                name="Section 1",
                farm=farm,
            ),
            domain.Section(
                id=2,
                name="Section 2",
                farm=farm,
            ),
        ]

        events = stallkarte.assign_rearing_farm(farm=farm)
        started_aggregator.apply_all(events)

        events = stallkarte.record_mortality(
            production_day=1,
            section_number=1,
            natural_deaths=1,
            selective_deaths=2,
            shift=MortalityRecordedShift.MORNING,
        )

        assert len(events) == 1
        event = events[0]

        assert event.type == stallkarte_events.MortalityRecorded.type()
        assert isinstance(event.data, stallkarte_events.MortalityRecorded)
        data = event.data

        assert data.production_day == 1
        assert data.section_number == 1
        assert data.natural_deaths == 1
        assert data.selective_deaths == 2
        assert data.shift == MortalityRecordedShift.MORNING

    @staticmethod
    def test_records_mortality_during_fattening(
        started_aggregator: domain.StallkarteAggregator,
        holding: domain.AgriculturalHolding,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        farm = domain.Farm(
            holding=holding,
            id=1,
            vvvo_number="VV100000",
            name="Fattening Farm 1",
            type=domain.FarmType.FATTENING,
            sections=[],
        )
        farm.sections = [
            domain.Section(
                id=1,
                name="Section 1",
                farm=farm,
            ),
            domain.Section(
                id=2,
                name="Section 2",
                farm=farm,
            ),
        ]

        events = stallkarte.assign_fattening_farm(farm=farm)
        started_aggregator.apply_all(events)

        events = stallkarte.transfer_flock(
            transfer_date=datetime.date.today(),
            animals_by_section_number={1: 2000, 2: 3000},
        )
        started_aggregator.apply_all(events)

        events = stallkarte.record_mortality(
            production_day=1,
            section_number=1,
            natural_deaths=3,
            selective_deaths=4,
            shift=MortalityRecordedShift.EVENING,
        )

        assert len(events) == 1
        event = events[0]

        assert event.type == stallkarte_events.MortalityRecorded.type()
        assert isinstance(event.data, stallkarte_events.MortalityRecorded)
        data = event.data

        assert data.production_day == 1
        assert data.section_number == 1
        assert data.natural_deaths == 3
        assert data.selective_deaths == 4
        assert data.shift == MortalityRecordedShift.EVENING

    @staticmethod
    def test_fails_if_production_day_is_negative(
        started_aggregator: domain.StallkarteAggregator,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        with pytest.raises(domain.Exception) as exc_info:
            stallkarte.record_mortality(
                production_day=-1,
                section_number=1,
                natural_deaths=1,
                selective_deaths=2,
                shift=MortalityRecordedShift.MORNING,
            )

        e = exc_info.value
        assert e.message == "production_day must be non-negative"

    @staticmethod
    def test_fails_if_no_rearing_farm_is_assigned_during_rearing(
        started_aggregator: domain.StallkarteAggregator,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        with pytest.raises(domain.Exception) as exc_info:
            stallkarte.record_mortality(
                production_day=1,
                section_number=1,
                natural_deaths=1,
                selective_deaths=2,
                shift=MortalityRecordedShift.MORNING,
            )

        e = exc_info.value
        assert e.message == "no farm assigned for the current cycle"

    @staticmethod
    def test_fails_if_section_does_not_exist(
        started_aggregator: domain.StallkarteAggregator,
        holding: domain.AgriculturalHolding,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        farm = domain.Farm(
            holding=holding,
            id=1,
            vvvo_number="VV100000",
            name="Rearing Farm 1",
            type=domain.FarmType.REARING,
            sections=[],
        )
        farm.sections = [
            domain.Section(
                id=1,
                name="Section 1",
                farm=farm,
            ),
        ]

        events = stallkarte.assign_rearing_farm(farm=farm)
        started_aggregator.apply_all(events)

        with pytest.raises(domain.Exception) as exc_info:
            stallkarte.record_mortality(
                production_day=1,
                section_number=2,  # non-existent section
                natural_deaths=1,
                selective_deaths=2,
                shift=MortalityRecordedShift.MORNING,
            )

        e = exc_info.value
        assert e.message == "section number 2 does not exist"


class TestLogSectionNote:
    @staticmethod
    def test_logs_section_note(
        started_aggregator: domain.StallkarteAggregator,
        holding: domain.AgriculturalHolding,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        farm = domain.Farm(
            holding=holding,
            id=1,
            vvvo_number="VV100000",
            name="Rearing Farm 1",
            type=domain.FarmType.REARING,
            sections=[],
        )
        farm.sections = [
            domain.Section(
                id=1,
                name="Section 1",
                farm=farm,
            ),
        ]

        events = stallkarte.assign_rearing_farm(farm=farm)
        started_aggregator.apply_all(events)

        events = stallkarte.log_section_note(
            production_day=0,
            section_number=1,
            note="This is a note for section 1.",
        )

        assert len(events) == 1
        event = events[0]

        assert event.type == stallkarte_events.SectionNoteLogged.type()
        assert isinstance(event.data, stallkarte_events.SectionNoteLogged)
        data = event.data

        assert data.production_day == 0
        assert data.section_number == 1
        assert data.note == "This is a note for section 1."

    @staticmethod
    def test_fails_if_production_day_is_negative(
        started_aggregator: domain.StallkarteAggregator,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        with pytest.raises(domain.Exception) as exc_info:
            stallkarte.log_section_note(
                production_day=-1,
                section_number=1,
                note="This is a note for section 1.",
            )

        e = exc_info.value
        assert e.message == "production_day must be non-negative"

    @staticmethod
    def test_fails_if_no_rearing_farm_is_assigned(
        started_aggregator: domain.StallkarteAggregator,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        with pytest.raises(domain.Exception) as exc_info:
            stallkarte.log_section_note(
                production_day=0,
                section_number=1,
                note="This is a note for section 1.",
            )

        e = exc_info.value
        assert e.message == "no farm assigned for the current cycle"

    @staticmethod
    def test_fails_if_section_does_not_exist(
        started_aggregator: domain.StallkarteAggregator,
        holding: domain.AgriculturalHolding,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        farm = domain.Farm(
            holding=holding,
            id=1,
            vvvo_number="VV100000",
            name="Rearing Farm 1",
            type=domain.FarmType.REARING,
            sections=[],
        )
        farm.sections = [
            domain.Section(
                id=1,
                name="Section 1",
                farm=farm,
            ),
        ]

        events = stallkarte.assign_rearing_farm(farm=farm)
        started_aggregator.apply_all(events)

        with pytest.raises(domain.Exception) as exc_info:
            stallkarte.log_section_note(
                production_day=0,
                section_number=2,  # non-existent section
                note="This is a note for section 2.",
            )

        e = exc_info.value
        assert e.message == "section number 2 does not exist"


class TestFinish:
    @staticmethod
    def test_finishes(
        started_aggregator: domain.StallkarteAggregator,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        today = datetime.date.today()
        events = stallkarte.finish(date=today)

        assert len(events) == 1
        event = events[0]

        assert event.type == stallkarte_events.Finished.type()
        assert isinstance(event.data, stallkarte_events.Finished)
        data = event.data

        assert data.date == today

    @staticmethod
    def test_fails_if_stallkarte_already_finished(
        started_aggregator: domain.StallkarteAggregator,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        today = datetime.date.today()
        events = stallkarte.finish(date=today)
        started_aggregator.apply_all(events)

        with pytest.raises(domain.Exception) as exc_info:
            stallkarte.finish(date=today + datetime.timedelta(days=1))

        e = exc_info.value
        assert e.message == "stallkarte is already finished"


class TestPerformAlarmTest:
    @staticmethod
    def test_performs_alarm_test(
        started_aggregator: domain.StallkarteAggregator,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        events = stallkarte.perform_alarm_test(
            cycle=domain.StallkarteCycle.REARING,
            did_alarm_test=True,
            did_emergency_power_test=False,
        )

        assert len(events) == 1
        event = events[0]

        assert event.type == stallkarte_events.AlarmTestPerformed.type()
        assert isinstance(event.data, stallkarte_events.AlarmTestPerformed)
        data = event.data

        assert data.cycle == domain.StallkarteCycle.REARING
        assert data.did_alarm_test is True
        assert data.did_emergency_power_test is False


class TestPerformLightningProgram:
    @staticmethod
    def test_performs_lightning_program(
        started_aggregator: domain.StallkarteAggregator,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        events = stallkarte.perform_lighting_program(
            cycle=domain.StallkarteCycle.FATTENING,
            did_dark_period_test=True,
            had_divergence_due_to_vet=False,
        )

        assert len(events) == 1
        event = events[0]

        assert event.type == stallkarte_events.LightingProgramPerformed.type()
        assert isinstance(event.data, stallkarte_events.LightingProgramPerformed)
        data = event.data

        assert data.cycle == domain.StallkarteCycle.FATTENING
        assert data.did_dark_period_test is True
        assert data.had_divergence_due_to_vet is False


class TestApplyPestControlMeasures:
    @staticmethod
    def test_applies_pest_control_measures(
        started_aggregator: domain.StallkarteAggregator,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        events = stallkarte.apply_pest_control_measures(
            cycle=domain.StallkarteCycle.REARING,
            did_perform_pest_control=True,
            annotation="Applied measures for pest control.",
        )

        assert len(events) == 1
        event = events[0]

        assert event.type == stallkarte_events.PestControlMeasuresApplied.type()
        assert isinstance(event.data, stallkarte_events.PestControlMeasuresApplied)
        data = event.data

        assert data.cycle == domain.StallkarteCycle.REARING
        assert data.did_perform_pest_control is True
        assert data.annotation == "Applied measures for pest control."


class TestCleanSilo:
    @staticmethod
    def test_cleans_silo(
        started_aggregator: domain.StallkarteAggregator,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        today = datetime.date.today()

        events = stallkarte.clean_silo(
            cycle=domain.StallkarteCycle.FATTENING,
            date=today,
            detergent="Detergent X",
            dosis="100ml per 1000 liters",
        )

        assert len(events) == 1
        event = events[0]

        assert event.type == stallkarte_events.SiloCleaned.type()
        assert isinstance(event.data, stallkarte_events.SiloCleaned)
        data = event.data

        assert data.cycle == domain.StallkarteCycle.FATTENING
        assert data.date == today
        assert data.detergent == "Detergent X"
        assert data.dosis == "100ml per 1000 liters"


class TestDisinfectStable:
    @staticmethod
    def test_disinfects_stable(
        started_aggregator: domain.StallkarteAggregator,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        today = datetime.date.today()

        events = stallkarte.disinfect_stable(
            cycle=domain.StallkarteCycle.REARING,
            date=today,
            disinfectant="Disinfectant Y",
            dosis="200ml per 1000 liters",
        )

        assert len(events) == 1
        event = events[0]

        assert event.type == stallkarte_events.StableDisinfected.type()
        assert isinstance(event.data, stallkarte_events.StableDisinfected)
        data = event.data

        assert data.cycle == domain.StallkarteCycle.REARING
        assert data.date == today
        assert data.disinfectant == "Disinfectant Y"
        assert data.dosis == "200ml per 1000 liters"


class TestDisinfectWaterLine:
    @staticmethod
    def test_disinfects_water_line(
        started_aggregator: domain.StallkarteAggregator,
    ) -> None:
        stallkarte = started_aggregator.stallkarte

        today = datetime.date.today()

        events = stallkarte.disinfect_water_line(
            cycle=domain.StallkarteCycle.FATTENING,
            date=today,
            disinfectant="Disinfectant Z",
            dosis="150ml per 1000 liters",
        )

        assert len(events) == 1
        event = events[0]

        assert event.type == stallkarte_events.WaterLineDisinfected.type()
        assert isinstance(event.data, stallkarte_events.WaterLineDisinfected)
        data = event.data

        assert data.cycle == domain.StallkarteCycle.FATTENING
        assert data.date == today
        assert data.disinfectant == "Disinfectant Z"
        assert data.dosis == "150ml per 1000 liters"
