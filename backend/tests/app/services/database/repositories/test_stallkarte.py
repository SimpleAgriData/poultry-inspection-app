import datetime

from app import domain
from app.domain.stallkarte import events
from app.services.database.repositories import (
    StallkarteRepository,
)


class TestStallkarteRepository:
    @staticmethod
    def test_create_stallkarte(
        stallkarte_repository: StallkarteRepository,
        holding: domain.AgriculturalHolding,
    ) -> None:
        stallkarte = stallkarte_repository.create_stallkarte(holding.id)

        assert stallkarte.id > 0
        assert stallkarte.holding_id == holding.id
        assert not stallkarte.state.is_started
        assert not stallkarte.state.is_finished

        # Verify it can be retrieved
        retrieved = stallkarte_repository.get_stallkarte_by_id(stallkarte.id)
        assert retrieved is not None
        assert retrieved.id == stallkarte.id

    @staticmethod
    def test_get_stallkarte_by_id_not_found(
        stallkarte_repository: StallkarteRepository,
    ) -> None:
        retrieved = stallkarte_repository.get_stallkarte_by_id(99999)
        assert retrieved is None

    @staticmethod
    def test_add_event_and_rebuild_state(
        stallkarte_repository: StallkarteRepository,
        holding: domain.AgriculturalHolding,
    ) -> None:
        stallkarte = stallkarte_repository.create_stallkarte(holding.id)
        today = datetime.date.today()

        start_event = events.StallkarteStarted(
            date_started=today,
            date_hatched=today,
            hatchery_name="Test Hatchery",
            breed="Test Breed",
            fattening_cycle="Test Cycle",
            eco_control_number="Test Eco",
            is_eu_bio=True,
            is_naturland=False,
        ).event()

        stallkarte_repository.add_event(stallkarte.id, start_event)

        # Retrieve and check if state is rebuilt
        retrieved = stallkarte_repository.get_stallkarte_by_id(stallkarte.id)
        assert retrieved is not None
        assert retrieved.state.is_started is True
        assert retrieved.state.hatchery == "Test Hatchery"
        assert retrieved.state.breed == "Test Breed"
        assert retrieved.state.fattening_cycle == "Test Cycle"
        assert retrieved.state.eco_control_number == "Test Eco"
        assert retrieved.state.is_eu_bio is True
        assert retrieved.state.is_naturland is False
        assert retrieved.state.date_started == today
        assert retrieved.state.date_hatched == today

    @staticmethod
    def test_add_events_and_rebuild_state(
        stallkarte_repository: StallkarteRepository,
        holding: domain.AgriculturalHolding,
    ) -> None:
        stallkarte = stallkarte_repository.create_stallkarte(holding.id)
        today = datetime.date.today()

        start_event = events.StallkarteStarted(
            date_started=today,
            date_hatched=today,
            hatchery_name="Test Hatchery",
            breed="Test Breed",
            fattening_cycle="Test Cycle",
            eco_control_number="Test Eco",
            is_eu_bio=True,
            is_naturland=False,
        ).event()

        finished_event = events.Finished(
            date=today + datetime.timedelta(days=42)
        ).event()

        stallkarte_repository.add_events(stallkarte.id, [start_event, finished_event])

        # Retrieve and check if state is rebuilt
        retrieved = stallkarte_repository.get_stallkarte_by_id(stallkarte.id)
        assert retrieved is not None
        assert retrieved.state.is_started is True
        assert retrieved.state.is_finished is True

    @staticmethod
    def test_mark_finished(
        stallkarte_repository: StallkarteRepository,
        holding: domain.AgriculturalHolding,
    ) -> None:
        stallkarte = stallkarte_repository.create_stallkarte(holding.id)
        stallkarte_repository.mark_finished(stallkarte.id)

        # This only updates the DB model, the domain object is not updated in place
        # We need to re-fetch it to see the change
        retrieved = stallkarte_repository.get_stallkarte_by_id(stallkarte.id)
        assert retrieved is not None
        # The `finished` flag on the state is set by the `Finished` event,
        # but the `is_finished` on the DB model is set directly.
        # Let's check the shallow representation which reads from the model.
        shallow_list = stallkarte_repository.get_shallow_stallkarten_by_holding_id(
            holding.id
        )
        assert len(shallow_list) == 1
        assert shallow_list[0].is_finished is True

    @staticmethod
    def test_get_shallow_stallkarten_by_holding_id(
        stallkarte_repository: StallkarteRepository,
        holding: domain.AgriculturalHolding,
        other_holding: domain.AgriculturalHolding,
    ) -> None:
        # Create stallkarten for two different holdings
        sk1 = stallkarte_repository.create_stallkarte(holding.id)
        sk2 = stallkarte_repository.create_stallkarte(holding.id)
        stallkarte_repository.create_stallkarte(other_holding.id)

        # Mark one as finished
        stallkarte_repository.mark_finished(sk2.id)

        # Fetch for the first holding
        shallow_list = stallkarte_repository.get_shallow_stallkarten_by_holding_id(
            holding.id
        )

        assert len(shallow_list) == 2
        ids = {s.id for s in shallow_list}
        assert sk1.id in ids
        assert sk2.id in ids

        # Fetch for the other holding
        other_list = stallkarte_repository.get_shallow_stallkarten_by_holding_id(
            other_holding.id
        )
        assert len(other_list) == 1
