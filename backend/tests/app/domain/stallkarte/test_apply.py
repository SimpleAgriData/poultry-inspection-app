import datetime

import pytest

from app import domain
from app.domain import (
    AgriculturalHolding,
    StallkarteAggregator,
    StallkarteState,
)
from app.domain.stallkarte import StallkarteFarm
from app.domain.stallkarte.events.dailyevents.mortality_recorded import (
    MortalityRecordedShift,
)
from app.domain.stallkarte.events.models import (
    NoteEntry,
    NoteType,
    WeatherCondition,
)
from app.domain.stallkarte.stallkarte_state import StallkarteCycle
from app.services.database import FarmCandidate, FarmTypeCandidate
from app.services.database.repositories import FarmRepository


class TestStallkarteAggregator:
    @staticmethod
    def test_assign_raring_farm(
        aggregator: StallkarteAggregator, farm_repository: FarmRepository
    ) -> None:
        stallkarte = aggregator.stallkarte
        state = stallkarte.state

        target_rearing_farm = farm_repository.add_farm(
            stallkarte.holding_id,
            FarmCandidate(
                name="Rearing Farm",
                type=FarmTypeCandidate.REARING,
                vvvo_number="987654",
            ),
        )

        events = stallkarte.assign_rearing_farm(target_rearing_farm)

        assert state == StallkarteState.default()

        aggregator.apply_all(events)

        assert state.rearing_farm == StallkarteFarm(
            id=target_rearing_farm.id,
            name=target_rearing_farm.name,
            type=target_rearing_farm.type,
            vvvo_number=target_rearing_farm.vvvo_number,
            sections=[],
        )

    @staticmethod
    def test_assign_fattening_farm(
        aggregator: StallkarteAggregator, farm_repository: FarmRepository
    ) -> None:
        stallkarte = aggregator.stallkarte
        state = stallkarte.state

        target_fattening_farm = farm_repository.add_farm(
            stallkarte.holding_id,
            FarmCandidate(
                name="Rearing Farm",
                type=FarmTypeCandidate.FATTENING,
                vvvo_number="987654",
            ),
        )
        events = stallkarte.assign_fattening_farm(target_fattening_farm)

        assert state == StallkarteState.default()

        aggregator.apply_all(events)

        assert state.fattening_farm == StallkarteFarm(
            id=target_fattening_farm.id,
            name=target_fattening_farm.name,
            type=target_fattening_farm.type,
            vvvo_number=target_fattening_farm.vvvo_number,
            sections=[],
        )

    @staticmethod
    def test_start_stallkarte(aggregator: StallkarteAggregator) -> None:
        stallkarte = aggregator.stallkarte
        state = stallkarte.state

        date_hatched = datetime.date.today()
        date_started = datetime.date.today() - datetime.timedelta(days=21)

        events = stallkarte.start_stallkarte(
            date_started,
            date_hatched,
            "Hatchery",
            "A1",
            "42",
            "123321",
            True,
            False,
        )

        assert state == StallkarteState.default()

        aggregator.apply_all(events)

        assert state.date_started == date_started
        assert state.date_hatched == date_hatched
        assert state.hatchery == "Hatchery"
        assert state.breed == "A1"
        assert state.fattening_cycle == "42"
        assert state.eco_control_number == "123321"
        assert state.is_eu_bio
        assert not state.is_naturland

    @staticmethod
    def test_revise_details(aggregator: StallkarteAggregator) -> None:
        stallkarte = aggregator.stallkarte
        state = stallkarte.state

        date_hatched = datetime.date.today()
        date_started = datetime.date.today() - datetime.timedelta(days=21)

        # First start the stallkarte
        events = stallkarte.start_stallkarte(
            date_started,
            date_hatched,
            "Hatchery",
            "A1",
            "42",
            "123321",
            True,
            False,
        )

        aggregator.apply_all(events)

        # Now revise details
        new_date_hatched = date_hatched - datetime.timedelta(days=1)

        events = stallkarte.revise_details(
            new_date_hatched,
            "New Hatchery",
            "B2",
            "43",
            True,
            True,
        )

        aggregator.apply_all(events)

        assert state.date_hatched == new_date_hatched
        assert state.hatchery == "New Hatchery"
        assert state.breed == "B2"
        assert state.fattening_cycle == "43"
        assert state.is_eu_bio
        assert state.is_naturland

    @staticmethod
    def test_transfer_flock(
        aggregator: StallkarteAggregator, farm_repository: FarmRepository
    ) -> None:
        stallkarte = aggregator.stallkarte
        state = stallkarte.state

        target_fattening_farm = farm_repository.add_farm(
            stallkarte.holding_id,
            FarmCandidate(
                name="Rearing Farm",
                type=FarmTypeCandidate.FATTENING,
                vvvo_number="987654",
            ),
        )
        events = stallkarte.assign_fattening_farm(target_fattening_farm)
        aggregator.apply_all(events)

        start_date = stallkarte.state.date_started
        events = stallkarte.transfer_flock(start_date, {1: 4000, 2: 4000})

        aggregator.apply_all(events)

        assert state.current_cycle == StallkarteCycle.FATTENING
        assert state.transfer is not None
        assert state.transfer.date == start_date
        assert state.transfer.production_day == 0
        assert state.transfer.animals_by_section_number == {1: 4000, 2: 4000}

    @staticmethod
    def test_revise_transfer_details(
        aggregator: StallkarteAggregator, farm_repository: FarmRepository
    ) -> None:
        stallkarte = aggregator.stallkarte
        state = stallkarte.state

        target_fattening_farm = farm_repository.add_farm(
            stallkarte.holding_id,
            FarmCandidate(
                name="Rearing Farm",
                type=FarmTypeCandidate.FATTENING,
                vvvo_number="987654",
            ),
        )
        events = stallkarte.assign_fattening_farm(target_fattening_farm)
        aggregator.apply_all(events)

        start_date = stallkarte.state.date_started
        events = stallkarte.transfer_flock(start_date, {1: 4000, 2: 4000})

        aggregator.apply_all(events)

        assert state.transfer is not None
        assert state.transfer.date == start_date
        assert state.transfer.production_day == 0

        events = stallkarte.revise_transfer_details({1: 3500, 2: 4500})

        aggregator.apply_all(events)

        assert state.transfer is not None
        assert state.transfer.animals_by_section_number == {1: 3500, 2: 4500}

    @staticmethod
    def test_record_ambient_climate(aggregator: StallkarteAggregator) -> None:
        stallkarte = aggregator.stallkarte
        state = stallkarte.state

        events = stallkarte.record_ambient_climate(1, 23.5, 60.0)

        aggregator.apply_all(events)

        day = state.days[1]
        assert day.temperature_celsius == 23.5
        assert day.humidity_percent == 60.0

    @staticmethod
    def test_record_fattening_day_data(aggregator: StallkarteAggregator) -> None:
        stallkarte = aggregator.stallkarte
        state = stallkarte.state
        state.transfer = domain.StallkarteTransfer(
            date=datetime.date.today(),
            production_day=3,
            animals_by_section_number={1: 10},
        )

        events = stallkarte.record_fattening_day_data(
            production_day=3,
            opening_time="08:30",
            weather_conditions=[
                WeatherCondition.SUN,
                WeatherCondition.CLOUDY,
            ],
            veterinarian=True,
        )

        aggregator.apply_all(events)

        day = state.days[3]
        assert day.opening_time == "08:30"
        assert day.weather_conditions == [
            WeatherCondition.SUN,
            WeatherCondition.CLOUDY,
        ]
        assert day.veterinarian is True

    @staticmethod
    def test_record_feed_consumption(aggregator: StallkarteAggregator) -> None:
        stallkarte = aggregator.stallkarte
        state = stallkarte.state

        events = stallkarte.record_feed_consumption(1, 150.5)

        aggregator.apply_all(events)

        day = state.days[1]
        assert day.feed_consumption_kg == 150.5

    @staticmethod
    def test_save_general_notes(aggregator: StallkarteAggregator) -> None:
        stallkarte = aggregator.stallkarte

        events = stallkarte.save_general_notes(
            production_day=1,
            general_notes=[
                NoteEntry(
                    id="note-1",
                    note_type=NoteType.OTHER,
                    note_text="Some note",
                )
            ],
        )

        aggregator.apply_all(events)

        day = stallkarte.state.days[1]
        assert len(day.notes) == 1
        assert day.notes[0].id == "note-1"
        assert day.notes[0].note_type == NoteType.OTHER
        assert day.notes[0].note_text == "Some note"

    @staticmethod
    def test_save_finish_notes(aggregator: StallkarteAggregator) -> None:
        stallkarte = aggregator.stallkarte

        events = stallkarte.save_finish_notes(
            finish_notes=[
                NoteEntry(
                    id="finish-note-1",
                    note_type=NoteType.SLAUGHTER,
                    slaughter_animals_count=1200,
                )
            ],
        )

        aggregator.apply_all(events)

        assert len(stallkarte.state.finish_notes) == 1
        assert stallkarte.state.finish_notes[0].id == "finish-note-1"
        assert stallkarte.state.finish_notes[0].slaughter_animals_count == 1200

    @staticmethod
    def test_mortality_recorded(
        aggregator: StallkarteAggregator, holding: AgriculturalHolding
    ) -> None:
        stallkarte = aggregator.stallkarte
        state = stallkarte.state

        farm = domain.Farm(
            id=1,
            name="Rearing Farm 1",
            type=domain.FarmType.REARING,
            vvvo_number="RF-001",
            sections=[],
            holding=holding,
        )
        farm.sections = [
            domain.Section(id=1, name="Section 1", farm=farm),
        ]

        events = stallkarte.assign_rearing_farm(farm)

        aggregator.apply_all(events)

        assert len(state.days) == 0

        events = stallkarte.record_mortality(1, 1, 2, 1, MortalityRecordedShift.MORNING)

        aggregator.apply_all(events)

        section = state.days[1].sections[1]
        assert section.natural_mortality_morning == 2
        assert section.selective_mortality_morning == 1

    @staticmethod
    def test_log_section_note(
        aggregator: StallkarteAggregator, holding: AgriculturalHolding
    ) -> None:
        stallkarte = aggregator.stallkarte
        state = stallkarte.state

        farm = domain.Farm(
            id=1,
            name="Rearing Farm 1",
            type=domain.FarmType.REARING,
            vvvo_number="RF-001",
            sections=[],
            holding=holding,
        )
        farm.sections = [
            domain.Section(id=1, name="Section 1", farm=farm),
        ]

        events = stallkarte.assign_rearing_farm(farm)

        aggregator.apply_all(events)

        assert len(state.days) == 0

        events = stallkarte.log_section_note(1, 1, "Section note")

        aggregator.apply_all(events)

        section = state.days[1].sections[1]
        assert section.note == "Section note"

    @staticmethod
    def test_record_water_consumption(aggregator: StallkarteAggregator) -> None:
        stallkarte = aggregator.stallkarte
        state = stallkarte.state

        events = stallkarte.record_water_consumption(1, 500.0)

        aggregator.apply_all(events)

        day = state.days[1]
        assert day.water_consumption_liters == 500.0

    @staticmethod
    def test_record_weight(aggregator: StallkarteAggregator) -> None:
        stallkarte = aggregator.stallkarte
        state = stallkarte.state

        events = stallkarte.record_weight(1, 1.5)

        aggregator.apply_all(events)

        day = state.days[1]
        assert day.weight_grams == 1.5

    @staticmethod
    def test_finish(aggregator: StallkarteAggregator) -> None:
        stallkarte = aggregator.stallkarte
        state = stallkarte.state

        date_finished = datetime.date.today()
        events = stallkarte.finish(date_finished)

        aggregator.apply_all(events)

        assert state.is_finished
        assert state.date_finished == date_finished
        assert state.finish_notes == []

    @staticmethod
    def test_finish_with_finish_notes(aggregator: StallkarteAggregator) -> None:
        stallkarte = aggregator.stallkarte
        state = stallkarte.state

        date_finished = datetime.date.today()
        finish_notes = [
            NoteEntry(
                id="sl-1",
                note_type=NoteType.SLAUGHTER,
                slaughter_date=date_finished,
                slaughter_final_weight_kg=2.35,
                slaughterer_name="Steinfelder",
            ),
            NoteEntry(
                id="ca-1",
                note_type=NoteType.CATCHING,
                catching_time="06:30",
                catcher_name="Team A",
            ),
        ]
        events = stallkarte.finish(date_finished, finish_notes=finish_notes)

        aggregator.apply_all(events)

        assert state.is_finished
        assert state.date_finished == date_finished
        assert state.finish_notes == finish_notes

    @staticmethod
    def test_finish_already_finished(aggregator: StallkarteAggregator) -> None:
        stallkarte = aggregator.stallkarte
        state = stallkarte.state

        date_finished = datetime.date.today()
        # First finish
        events = stallkarte.finish(date_finished)
        aggregator.apply_all(events)

        assert state.is_finished

        with pytest.raises(domain.Exception, match="stallkarte is already finished"):
            stallkarte.finish(date_finished)

    @staticmethod
    def test_perform_alarm_test(aggregator: StallkarteAggregator) -> None:
        stallkarte = aggregator.stallkarte
        state = stallkarte.state

        events = stallkarte.perform_alarm_test(
            StallkarteCycle.REARING, did_alarm_test=True, did_emergency_power_test=False
        )
        aggregator.apply_all(events)

        assert state.rearing_checklist is not None
        assert state.rearing_checklist.alarm_test is not None
        assert state.rearing_checklist.alarm_test.did_alarm_test
        assert not state.rearing_checklist.alarm_test.did_emergency_power_test

        events = stallkarte.perform_alarm_test(
            StallkarteCycle.FATTENING,
            did_alarm_test=False,
            did_emergency_power_test=True,
        )
        aggregator.apply_all(events)

        assert state.fattening_checklist is not None
        assert state.fattening_checklist.alarm_test is not None
        assert not state.fattening_checklist.alarm_test.did_alarm_test
        assert state.fattening_checklist.alarm_test.did_emergency_power_test

    @staticmethod
    def test_perform_lighting_program(aggregator: StallkarteAggregator) -> None:
        stallkarte = aggregator.stallkarte
        state = stallkarte.state

        events = stallkarte.perform_lighting_program(
            StallkarteCycle.REARING,
            did_dark_period_test=True,
            had_divergence_due_to_vet=False,
        )
        aggregator.apply_all(events)

        assert state.rearing_checklist is not None
        assert state.rearing_checklist.lighting_program is not None
        assert state.rearing_checklist.lighting_program.did_dark_period_test
        assert not state.rearing_checklist.lighting_program.had_divergence_due_to_vet

        events = stallkarte.perform_lighting_program(
            StallkarteCycle.FATTENING,
            did_dark_period_test=False,
            had_divergence_due_to_vet=True,
        )
        aggregator.apply_all(events)

        assert state.fattening_checklist is not None
        assert state.fattening_checklist.lighting_program is not None
        assert not state.fattening_checklist.lighting_program.did_dark_period_test
        assert state.fattening_checklist.lighting_program.had_divergence_due_to_vet

    @staticmethod
    def test_apply_pest_control_measures(aggregator: StallkarteAggregator) -> None:
        stallkarte = aggregator.stallkarte
        state = stallkarte.state

        events = stallkarte.apply_pest_control_measures(
            cycle=StallkarteCycle.REARING,
            did_perform_pest_control=True,
            annotation="Applied pest control measures",
        )
        aggregator.apply_all(events)

        assert state.rearing_checklist is not None
        assert state.rearing_checklist.pest_control_measures is not None
        assert state.rearing_checklist.pest_control_measures.did_perform_pest_control
        assert (
            state.rearing_checklist.pest_control_measures.annotation
            == "Applied pest control measures"
        )

        events = stallkarte.apply_pest_control_measures(
            cycle=StallkarteCycle.FATTENING,
            did_perform_pest_control=False,
            annotation="Applied pest control measures",
        )
        aggregator.apply_all(events)

        assert state.fattening_checklist is not None
        assert state.fattening_checklist.pest_control_measures is not None
        assert (
            not state.fattening_checklist.pest_control_measures.did_perform_pest_control
        )
        assert (
            state.fattening_checklist.pest_control_measures.annotation
            == "Applied pest control measures"
        )

    @staticmethod
    def test_clean_silo(
        aggregator: StallkarteAggregator,
    ) -> None:
        stallkarte = aggregator.stallkarte
        state = stallkarte.state

        today = datetime.date.today()
        events = stallkarte.clean_silo(
            cycle=StallkarteCycle.REARING,
            date=today,
            detergent="Detergent A",
            dosis="Dosis A",
        )
        aggregator.apply_all(events)

        assert state.rearing_checklist is not None
        assert state.rearing_checklist.silo_cleaned is not None
        assert state.rearing_checklist.silo_cleaned.date == today
        assert state.rearing_checklist.silo_cleaned.detergent == "Detergent A"
        assert state.rearing_checklist.silo_cleaned.dosis == "Dosis A"

        events = stallkarte.clean_silo(
            cycle=StallkarteCycle.FATTENING,
            date=today,
            detergent="Detergent B",
            dosis="Dosis B",
        )
        aggregator.apply_all(events)

        assert state.fattening_checklist is not None
        assert state.fattening_checklist.silo_cleaned is not None
        assert state.fattening_checklist.silo_cleaned.date == today
        assert state.fattening_checklist.silo_cleaned.detergent == "Detergent B"
        assert state.fattening_checklist.silo_cleaned.dosis == "Dosis B"

    @staticmethod
    def test_disinfect_stable(aggregator: StallkarteAggregator) -> None:
        stallkarte = aggregator.stallkarte
        state = stallkarte.state

        today = datetime.date.today()
        events = stallkarte.disinfect_stable(
            cycle=StallkarteCycle.REARING,
            date=today,
            disinfectant="Disinfectant A",
            dosis="Dosis A",
        )
        aggregator.apply_all(events)

        assert state.rearing_checklist is not None
        assert state.rearing_checklist.stable_disinfected is not None
        assert state.rearing_checklist.stable_disinfected.date == today
        assert (
            state.rearing_checklist.stable_disinfected.disinfectant == "Disinfectant A"
        )
        assert state.rearing_checklist.stable_disinfected.dosis == "Dosis A"

        events = stallkarte.disinfect_stable(
            cycle=StallkarteCycle.FATTENING,
            date=today,
            disinfectant="Disinfectant B",
            dosis="Dosis B",
        )
        aggregator.apply_all(events)

        assert state.fattening_checklist is not None
        assert state.fattening_checklist.stable_disinfected is not None
        assert state.fattening_checklist.stable_disinfected.date == today
        assert (
            state.fattening_checklist.stable_disinfected.disinfectant
            == "Disinfectant B"
        )
        assert state.fattening_checklist.stable_disinfected.dosis == "Dosis B"

    @staticmethod
    def test_disinfect_water_line(aggregator: StallkarteAggregator) -> None:
        stallkarte = aggregator.stallkarte
        state = stallkarte.state

        today = datetime.date.today()
        events = stallkarte.disinfect_water_line(
            cycle=StallkarteCycle.REARING,
            date=today,
            disinfectant="Disinfectant A",
            dosis="Dosis A",
        )
        aggregator.apply_all(events)

        assert state.rearing_checklist is not None
        assert state.rearing_checklist.water_line_disinfected is not None
        assert state.rearing_checklist.water_line_disinfected.date == today
        assert (
            state.rearing_checklist.water_line_disinfected.disinfectant
            == "Disinfectant A"
        )
        assert state.rearing_checklist.water_line_disinfected.dosis == "Dosis A"

        events = stallkarte.disinfect_water_line(
            cycle=StallkarteCycle.FATTENING,
            date=today,
            disinfectant="Disinfectant B",
            dosis="Dosis B",
        )
        aggregator.apply_all(events)

        assert state.fattening_checklist is not None
        assert state.fattening_checklist.water_line_disinfected is not None
        assert state.fattening_checklist.water_line_disinfected.date == today
        assert (
            state.fattening_checklist.water_line_disinfected.disinfectant
            == "Disinfectant B"
        )
        assert state.fattening_checklist.water_line_disinfected.dosis == "Dosis B"
