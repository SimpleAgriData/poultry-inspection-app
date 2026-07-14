from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.mixins import Base, SoftDeletableMixin

if TYPE_CHECKING:
    from app.db.models import AgriculturalHolding, Section


class FarmType(StrEnum):
    FATTENING = "fattening"
    REARING = "rearing"
    COMBINED = "combined"


class Farm(SoftDeletableMixin, Base):
    __tablename__ = "farm"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[FarmType] = mapped_column(Enum(FarmType), nullable=False)
    name: Mapped[str]
    vvvo_number: Mapped[str]

    holding_id: Mapped[int] = mapped_column(ForeignKey("agricultural_holding.id"))
    holding: Mapped["AgriculturalHolding"] = relationship(
        "AgriculturalHolding", back_populates="farms"
    )

    sections: Mapped[list["Section"]] = relationship(
        "Section", back_populates="farm", cascade="all, delete-orphan"
    )
