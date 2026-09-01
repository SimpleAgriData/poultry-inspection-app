from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.mixins import Base

if TYPE_CHECKING:
    from app.db.models import Farm


class AgriculturalHolding(Base):
    __tablename__ = "agricultural_holding"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_user_id: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str]
    hatchery: Mapped[str]
    eco_control_number: Mapped[str]
    breed: Mapped[str] = mapped_column(ForeignKey("chicken_breed.label"))
    address_street: Mapped[str]
    address_zip: Mapped[str]
    address_city: Mapped[str]

    farms: Mapped[list["Farm"]] = relationship(
        "Farm", back_populates="holding", cascade="all, delete-orphan"
    )
