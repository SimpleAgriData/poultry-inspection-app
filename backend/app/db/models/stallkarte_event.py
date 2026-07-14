import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.mixins import Base

if TYPE_CHECKING:
    from app.db.models import Stallkarte


class StallkarteEvent(Base):
    __tablename__ = "stallkarte_event"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    stallkarte_id: Mapped[int] = mapped_column(ForeignKey("stallkarte.id"))
    stallkarte: Mapped["Stallkarte"] = relationship(
        "Stallkarte", back_populates="events"
    )

    type: Mapped[str] = mapped_column("type", Text)
    data: Mapped[str] = mapped_column("data", Text)
    date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
