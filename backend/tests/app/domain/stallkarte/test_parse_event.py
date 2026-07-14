import datetime

import pytest
from pydantic import ValidationError

from app.domain.stallkarte import events, parse_event
from app.domain.stallkarte.event import Event
from app.domain.stallkarte.events import models
from app.domain.stallkarte.events.dailyevents.mortality_recorded import (
    MortalityRecordedShift,
)

type EventType = str
type EventPayload = str


class TestParseEvent:
    @staticmethod
    def test_parse_stallkarte_started_event() -> None:
        event_type: EventType = "stallkarte.stallkarte_started"
        event_payload: EventPayload = """
        {
            "date_started": "2024-01-01",
            "date_hatched": "2023-12-25",
            "hatchery_name": "Best Hatchery",
            "breed": "Broiler",
            "fattening_cycle": "Cycle 1",
            "eco_control_number": "EC12345",
            "is_eu_bio": true,
            "is_naturland": false
        }
        """

        expected_event = Event(
            type=event_type,
            data=events.StallkarteStarted(
                date_started=datetime.date(2024, 1, 1),
                date_hatched=datetime.date(2023, 12, 25),
                hatchery_name="Best Hatchery",
                breed="Broiler",
                fattening_cycle="Cycle 1",
                eco_control_number="EC12345",
                is_eu_bio=True,
                is_naturland=False,
            ),
        )

        parsed_event = parse_event(event_type, event_payload)
        assert parsed_event == expected_event

    @staticmethod
    def test_parse_details_revised_event() -> None:
        event_type: EventType = "stallkarte.details_revised"
        event_payload: EventPayload = """
        {
            "date_hatched": "2023-12-25",
            "hatchery_name": "Best Hatchery",
            "breed": "Broiler",
            "fattening_cycle": "Cycle 1",
            "is_eu_bio": true,
            "is_naturland": false
        }
        """

        expected_event = Event(
            type=event_type,
            data=events.DetailsRevised(
                date_hatched=datetime.date(2023, 12, 25),
                hatchery_name="Best Hatchery",
                breed="Broiler",
                fattening_cycle="Cycle 1",
                is_eu_bio=True,
                is_naturland=False,
            ),
        )

        parsed_event = parse_event(event_type, event_payload)
        assert parsed_event == expected_event

    @staticmethod
    def test_parse_rearing_farm_assigned_event() -> None:
        event_type: EventType = "stallkarte.rearing_farm_assigned"
        event_payload: EventPayload = """
        {
            "farm_id": 1,
            "farm_name": "Rearing Farm A",
            "farm_type": "rearing",
            "farm_vvvo_number": "VVVO123",
            "sections": [
                {
                    "id": 1,
                    "number": 1,
                    "name": "Section A"
                }
            ]
        }
        """

        expected_event = Event(
            type=event_type,
            data=events.RearingFarmAssigned(
                farm_id=1,
                farm_name="Rearing Farm A",
                farm_type=models.AssignedFarmType.REARING,
                farm_vvvo_number="VVVO123",
                sections=[
                    models.AssignedFarmSection(
                        id=1,
                        number=1,
                        name="Section A",
                    )
                ],
            ),
        )

        parsed_event = parse_event(event_type, event_payload)
        assert parsed_event == expected_event

    @staticmethod
    def test_parse_fattening_farm_assigned_event() -> None:
        event_type: EventType = "stallkarte.fattening_farm_assigned"
        event_payload: EventPayload = """
        {
            "farm_id": 2,
            "farm_name": "Fattening Farm B",
            "farm_type": "fattening",
            "farm_vvvo_number": "VVVO456",
            "sections": [
                {
                    "id": 2,
                    "number": 2,
                    "name": "Section B"
                }
            ]
        }
        """

        expected_event = Event(
            type=event_type,
            data=events.FatteningFarmAssigned(
                farm_id=2,
                farm_name="Fattening Farm B",
                farm_type=models.AssignedFarmType.FATTENING,
                farm_vvvo_number="VVVO456",
                sections=[
                    models.AssignedFarmSection(
                        id=2,
                        number=2,
                        name="Section B",
                    )
                ],
            ),
        )

        parsed_event = parse_event(event_type, event_payload)
        assert parsed_event == expected_event

    @staticmethod
    def test_parse_flock_transferred_event() -> None:
        event_type: EventType = "stallkarte.flock_transferred"
        event_payload: EventPayload = """
        {
            "transfer_date": "2024-01-15",
            "animals_by_section": {
                "1": 100,
                "2": 100
            }
        }
        """

        expected_event = Event(
            type=event_type,
            data=events.FlockTransferred(
                transfer_date=datetime.date(2024, 1, 15),
                animals_by_section={
                    1: 100,
                    2: 100,
                },
            ),
        )

        parsed_event = parse_event(event_type, event_payload)
        assert parsed_event == expected_event

    @staticmethod
    def test_parse_transfer_details_revised_event() -> None:
        event_type: EventType = "stallkarte.transfer_details_revised"
        event_payload: EventPayload = """
        {
            "animals_by_section": {
                "1": 90,
                "2": 110
            }
        }
        """

        expected_event = Event(
            type=event_type,
            data=events.TransferDetailsRevised(
                animals_by_section={
                    1: 90,
                    2: 110,
                },
            ),
        )

        parsed_event = parse_event(event_type, event_payload)
        assert parsed_event == expected_event

    @staticmethod
    def test_parse_feed_consumption_recorded_event() -> None:
        event_type: EventType = "stallkarte.feed_consumption_recorded"
        event_payload: EventPayload = """
        {
            "production_day": 10,
            "amount_kg": 500.0
        }
        """

        expected_event = Event(
            type=event_type,
            data=events.FeedConsumptionRecorded(
                production_day=10,
                amount_kg=500.0,
            ),
        )

        parsed_event = parse_event(event_type, event_payload)
        assert parsed_event == expected_event

    @staticmethod
    def test_parse_water_consumption_recorded_event() -> None:
        event_type: EventType = "stallkarte.water_consumption_recorded"
        event_payload: EventPayload = """
        {
            "production_day": 10,
            "amount_liters": 1000.0
        }
        """

        expected_event = Event(
            type=event_type,
            data=events.WaterConsumptionRecorded(
                production_day=10,
                amount_liters=1000.0,
            ),
        )

        parsed_event = parse_event(event_type, event_payload)
        assert parsed_event == expected_event

    @staticmethod
    def test_parse_weight_recorded_event() -> None:
        event_type: EventType = "stallkarte.weight_recorded"
        event_payload: EventPayload = """
        {
            "production_day": 10,
            "weight_grams": 1500.0
        }
        """

        expected_event = Event(
            type=event_type,
            data=events.WeightRecorded(
                production_day=10,
                weight_grams=1500.0,
            ),
        )

        parsed_event = parse_event(event_type, event_payload)
        assert parsed_event == expected_event

    @staticmethod
    def test_parse_ambient_climate_recorded_event() -> None:
        event_type: EventType = "stallkarte.ambient_climate_recorded"
        event_payload: EventPayload = """
        {
            "production_day": 1,
            "temperature_celsius": 22.5,
            "humidity_percent": 60.0
        }
        """

        expected_event = Event(
            type=event_type,
            data=events.AmbientClimateRecorded(
                production_day=1,
                temperature_celsius=22.5,
                humidity_percent=60.0,
            ),
        )

        parsed_event = parse_event(event_type, event_payload)
        assert parsed_event == expected_event

    @staticmethod
    def test_parse_fattening_day_data_recorded_event() -> None:
        event_type: EventType = "stallkarte.fattening_day_data_recorded"
        event_payload: EventPayload = """
        {
            "production_day": 20,
            "opening_time": "08:15",
            "weather_conditions": ["sun", "frost"],
            "veterinarian": true
        }
        """

        expected_event = Event(
            type=event_type,
            data=events.FatteningDayDataRecorded(
                production_day=20,
                opening_time="08:15",
                weather_conditions=[
                    models.WeatherCondition.SUN,
                    models.WeatherCondition.FROST,
                ],
                veterinarian=True,
            ),
        )

        parsed_event = parse_event(event_type, event_payload)
        assert parsed_event == expected_event

    @staticmethod
    def test_parse_mortality_recorded_event() -> None:
        event_type: EventType = "stallkarte.mortality_recorded"
        event_payload: EventPayload = """
        {
            "production_day": 1,
            "section_number": 2,
            "shift": "morning",
            "natural_deaths": 3,
            "selective_deaths": 2
        }
        """

        expected_event = Event(
            type=event_type,
            data=events.MortalityRecorded(
                production_day=1,
                section_number=2,
                shift=MortalityRecordedShift.MORNING,
                natural_deaths=3,
                selective_deaths=2,
            ),
        )

        parsed_event = parse_event(event_type, event_payload)
        assert parsed_event == expected_event

    @staticmethod
    def test_parse_section_note_logged_event() -> None:
        event_type: EventType = "stallkarte.section_note_logged"
        event_payload: EventPayload = """
        {
            "production_day": 1,
            "section_number": 2,
            "note": "This is a note about section 2."
        }
        """

        expected_event = Event(
            type=event_type,
            data=events.SectionNoteLogged(
                production_day=1,
                section_number=2,
                note="This is a note about section 2.",
            ),
        )

        parsed_event = parse_event(event_type, event_payload)
        assert parsed_event == expected_event

    @staticmethod
    def test_parse_finished_event() -> None:
        event_type: EventType = "stallkarte.finished"
        event_payload: EventPayload = """
        {
            "date": "2024-02-15"
        }
        """

        expected_event = Event(
            type=event_type,
            data=events.Finished(
                date=datetime.date(2024, 2, 15),
            ),
        )

        parsed_event = parse_event(event_type, event_payload)
        assert parsed_event == expected_event

    @staticmethod
    def test_parse_finished_event_with_finish_notes() -> None:
        event_type: EventType = "stallkarte.finished"
        event_payload: EventPayload = """
        {
            "date": "2024-02-15",
            "finish_notes": [
                {
                    "id": "sl-1",
                    "note_type": "slaughter",
                    "slaughter_date": "2024-02-15",
                    "slaughter_animals_count": 1200,
                    "slaughter_final_weight_kg": 2.4,
                    "slaughterer_name": "Steinfelder"
                },
                {
                    "id": "ca-1",
                    "note_type": "catching",
                    "catching_time": "05:45",
                    "catcher_name": "Team Nord"
                }
            ]
        }
        """

        expected_event = Event(
            type=event_type,
            data=events.Finished(
                date=datetime.date(2024, 2, 15),
                finish_notes=[
                    models.NoteEntry(
                        id="sl-1",
                        note_type=models.NoteType.SLAUGHTER,
                        slaughter_date=datetime.date(2024, 2, 15),
                        slaughter_animals_count=1200,
                        slaughter_final_weight_kg=2.4,
                        slaughterer_name="Steinfelder",
                    ),
                    models.NoteEntry(
                        id="ca-1",
                        note_type=models.NoteType.CATCHING,
                        catching_time="05:45",
                        catcher_name="Team Nord",
                    ),
                ],
            ),
        )

        parsed_event = parse_event(event_type, event_payload)
        assert parsed_event == expected_event

    @staticmethod
    def test_parse_finish_notes_replaced_event() -> None:
        event_type: EventType = "stallkarte.finish_notes_replaced"
        event_payload: EventPayload = """
        {
            "finish_notes": [
                {
                    "id": "sl-1",
                    "note_type": "slaughter",
                    "slaughter_animals_count": 1200
                }
            ]
        }
        """

        expected_event = Event(
            type=event_type,
            data=events.FinishNotesReplaced(
                finish_notes=[
                    models.NoteEntry(
                        id="sl-1",
                        note_type=models.NoteType.SLAUGHTER,
                        slaughter_animals_count=1200,
                    )
                ]
            ),
        )

        parsed_event = parse_event(event_type, event_payload)
        assert parsed_event == expected_event

    @staticmethod
    def test_alarm_test_performed_event() -> None:
        event_type: EventType = "stallkarte.alarm_test_performed"
        event_payload: EventPayload = """
        {
            "did_alarm_test": true,
            "did_emergency_power_test": false,
            "cycle": "rearing"
        }
        """

        expected_event = Event(
            type=event_type,
            data=events.AlarmTestPerformed(
                did_alarm_test=True,
                did_emergency_power_test=False,
                cycle=models.ChecklistCycle.REARING,
            ),
        )

        parsed_event = parse_event(event_type, event_payload)
        assert parsed_event == expected_event

    @staticmethod
    def test_lighting_program_performed_event() -> None:
        event_type: EventType = "stallkarte.lighting_program_performed"
        event_payload: EventPayload = """
        {
            "cycle": "fattening",
            "did_dark_period_test": false,
            "had_divergence_due_to_vet": true
        }
        """

        expected_event = Event(
            type=event_type,
            data=events.LightingProgramPerformed(
                cycle=models.ChecklistCycle.FATTENING,
                did_dark_period_test=False,
                had_divergence_due_to_vet=True,
            ),
        )

        parsed_event = parse_event(event_type, event_payload)
        assert parsed_event == expected_event

    @staticmethod
    def test_pest_control_measures_applied_event() -> None:
        event_type: EventType = "stallkarte.pest_control_measures_applied"
        event_payload: EventPayload = """
        {
            "cycle": "rearing",
            "did_perform_pest_control": true,
            "annotation": "Measure 1, Measure 2"
        }
        """

        expected_event = Event(
            type=event_type,
            data=events.PestControlMeasuresApplied(
                cycle=models.ChecklistCycle.REARING,
                did_perform_pest_control=True,
                annotation="Measure 1, Measure 2",
            ),
        )

        parsed_event = parse_event(event_type, event_payload)
        assert parsed_event == expected_event

    @staticmethod
    def test_silo_cleaned_event() -> None:
        event_type: EventType = "stallkarte.silo_cleaned"
        event_payload: EventPayload = """
        {
            "cycle": "fattening",
            "date": "2024-01-20",
            "detergent": "Detergent A",
            "dosis": "10 liters"
        }
        """

        expected_event = Event(
            type=event_type,
            data=events.SiloCleaned(
                cycle=models.ChecklistCycle.FATTENING,
                date=datetime.date(2024, 1, 20),
                detergent="Detergent A",
                dosis="10 liters",
            ),
        )

        parsed_event = parse_event(event_type, event_payload)
        assert parsed_event == expected_event

    @staticmethod
    def test_stable_disinfected_event() -> None:
        event_type: EventType = "stallkarte.stable_disinfected"
        event_payload: EventPayload = """
        {
            "cycle": "rearing",
            "date": "2024-01-25",
            "disinfectant": "Disinfectant B",
            "dosis": "5 liters"
        }
        """

        expected_event = Event(
            type=event_type,
            data=events.StableDisinfected(
                cycle=models.ChecklistCycle.REARING,
                date=datetime.date(2024, 1, 25),
                disinfectant="Disinfectant B",
                dosis="5 liters",
            ),
        )

        parsed_event = parse_event(event_type, event_payload)
        assert parsed_event == expected_event

    @staticmethod
    def test_water_line_disinfected_event() -> None:
        event_type: EventType = "stallkarte.water_line_disinfected"
        event_payload: EventPayload = """
        {
            "cycle": "fattening",
            "date": "2024-01-30",
            "disinfectant": "Disinfectant C",
            "dosis": "3 liters"
        }
        """

        expected_event = Event(
            type=event_type,
            data=events.WaterLineDisinfected(
                cycle=models.ChecklistCycle.FATTENING,
                date=datetime.date(2024, 1, 30),
                disinfectant="Disinfectant C",
                dosis="3 liters",
            ),
        )

        parsed_event = parse_event(event_type, event_payload)
        assert parsed_event == expected_event

    @staticmethod
    def test_fails_with_unknown_event_type() -> None:
        event_type: EventType = "stallkarte.unknown_event"
        event_payload: EventPayload = """
        {
            "some_field": "some_value"
        }
        """

        with pytest.raises(
            ValueError, match=r"unknown event type stallkarte.unknown_event"
        ):
            parse_event(event_type, event_payload)

    @staticmethod
    def test_fails_with_invalid_payload() -> None:
        event_type: EventType = "stallkarte.stallkarte_started"
        event_payload: EventPayload = """
        {
            "date_started": "invalid_date",
            "date_hatched": "2023-12-25",
            "initial_number_of_animals_per_section": 100,
            "hatchery_name": "Best Hatchery",
            "breed": "Broiler",
            "production_week": 1,
            "parent_flock": "Flock A",
            "fattening_cycle": "Cycle 1",
            "eco_control_number": "EC12345",
            "is_eu_bio": true,
            "is_naturland": false
        }
        """

        with pytest.raises(ValidationError) as exc_info:
            parse_event(event_type, event_payload)

        e = exc_info.value
        assert len(e.errors()) == 1
        assert e.errors()[0]["loc"] == ("date_started",)
        assert (
            e.errors()[0]["msg"]
            == "Input should be a valid date or datetime, invalid character in year"
        )
