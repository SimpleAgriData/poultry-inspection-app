import abc
import datetime

from sqlalchemy.orm import Session

from app.db.models.mixins import SoftDeletableMixin


class Repository(abc.ABC):
    def __init__(self, session: Session) -> None:
        self.session = session

    def _add(self, instance: object) -> None:
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)

    def _delete(self, instance: object) -> None:
        if isinstance(instance, SoftDeletableMixin):
            instance.deleted_at = datetime.datetime.now(datetime.timezone.utc)
            self.session.add(instance)
        else:
            self.session.delete(instance)
        self.session.commit()
