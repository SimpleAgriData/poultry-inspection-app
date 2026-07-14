from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.mixins import Base, SoftDeletableMixin

if TYPE_CHECKING:
    from app.db.models import AgriculturalHolding, StallkarteEvent


class Stallkarte(Base, SoftDeletableMixin):
    __tablename__ = "stallkarte"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    is_finished: Mapped[bool] = mapped_column(default=False)
    holding_id: Mapped[int] = mapped_column(ForeignKey("agricultural_holding.id"))
    holding: Mapped["AgriculturalHolding"] = relationship(
        "AgriculturalHolding",
        # back_populates="stallkarten",
    )

    events: Mapped[list["StallkarteEvent"]] = relationship(
        "StallkarteEvent",
        back_populates="stallkarte",
        cascade="all, delete-orphan",
    )
