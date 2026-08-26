import datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import contains_eager

from app import domain
from app.db import models
from app.domain.stallkarte import events
from app.services.database import translate
from app.services.database.repositories.repository import Repository


class StallkarteRepository(Repository):
    def create_stallkarte(
        self, holding_id: int, commit: bool = True
    ) -> domain.Stallkarte:
        db_stallkarte = models.Stallkarte(
            holding_id=holding_id,
        )
        self._add(db_stallkarte, commit=commit)

        return translate.stallkarte_to_domain(db_stallkarte)

    def add_event(
        self, stallkarte_id: int, event: domain.StallkarteEvent, commit: bool = True
    ) -> None:
        self.add_events(stallkarte_id, [event], commit=commit)

    def add_events(
        self,
        stallkarte_id: int,
        events_to_add: list[domain.StallkarteEvent],
        commit: bool = True,
    ) -> None:
        db_events: list[models.StallkarteEvent] = []
        for event in events_to_add:
            db_events.append(
                models.StallkarteEvent(
                    stallkarte_id=stallkarte_id,
                    type=event.type,
                    data=event.data.model_dump_json(),
                    date=datetime.datetime.now(datetime.timezone.utc),
                )
            )
        self.session.add_all(db_events)
        if commit:
            self.session.commit()

    def get_stallkarte_by_id(self, stallkarte_id: int) -> domain.Stallkarte | None:
        statement = (
            select(models.Stallkarte)
            # isouter, since some stallkarten might not have events yet, but we still
            # want to be able to retrieve them.
            .join(models.StallkarteEvent, isouter=True)
            .options(contains_eager(models.Stallkarte.events))
            .where(
                models.Stallkarte.id == stallkarte_id,
            )
            .order_by(models.StallkarteEvent.date.asc())
        )
        db_stallkarte = self.session.execute(statement).unique().scalar_one_or_none()

        if db_stallkarte is None:
            return None

        return translate.stallkarte_to_domain(db_stallkarte)

    def mark_finished(self, stallkarte_id: int, commit: bool = True) -> None:
        statement = select(models.Stallkarte).where(
            models.Stallkarte.id == stallkarte_id,
        )
        db_stallkarte = self.session.execute(statement).scalar_one_or_none()

        if db_stallkarte is None:
            raise ValueError(f"stallkarte with ID '{stallkarte_id}' not found")

        db_stallkarte.is_finished = True
        self._add(db_stallkarte, commit=commit)

    def mark_reopened(self, stallkarte_id: int) -> None:
        statement = select(models.Stallkarte).where(
            models.Stallkarte.id == stallkarte_id,
        )
        db_stallkarte = self.session.execute(statement).scalar_one_or_none()

        if db_stallkarte is None:
            raise ValueError(f"stallkarte with ID '{stallkarte_id}' not found")

        db_stallkarte.is_finished = False
        self._add(db_stallkarte)

    def delete_stallkarte(self, stallkarte_id: int) -> None:
        statement = select(models.Stallkarte).where(
            models.Stallkarte.id == stallkarte_id,
        )
        db_stallkarte = self.session.execute(statement).scalar_one_or_none()

        if db_stallkarte is None:
            raise ValueError(f"stallkarte with ID '{stallkarte_id}' not found")

        self._delete(db_stallkarte)

    def get_shallow_stallkarten_by_holding_id(
        self, holding_id: int
    ) -> list[domain.ShallowStallkarte]:
        # Select only the stallkarte_started event for each stallkarte for the
        # most essential information to display in the overview.
        statement = (
            select(models.Stallkarte)
            .join(
                models.StallkarteEvent,
                # This explicit join is necessary to filter the events on join and not
                # in the where clause, which would filter the stallkarten instead.
                and_(
                    models.StallkarteEvent.stallkarte_id == models.Stallkarte.id,
                    or_(
                        models.StallkarteEvent.type == events.StallkarteStarted.type(),
                        models.StallkarteEvent.type == events.Finished.type(),
                        models.StallkarteEvent.type == events.DetailsRevised.type(),
                    ),
                ),
                # some stallkarten might not have events yet, but we still
                # want to be able to retrieve them.
                isouter=True,
            )
            .options(contains_eager(models.Stallkarte.events))
            .where(
                models.Stallkarte.holding_id == holding_id,
            )
            .order_by(models.StallkarteEvent.date.asc())
        )

        db_stallkarten = self.session.execute(statement).unique().scalars().all()

        stallkarten: list[domain.ShallowStallkarte] = []

        for db_stallkarte in db_stallkarten:
            stallkarte = translate.shallow_stallkarte_to_domain(db_stallkarte)
            stallkarten.append(stallkarte)

        return stallkarten
