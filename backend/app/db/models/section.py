from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.mixins import Base, SoftDeletableMixin

if TYPE_CHECKING:
    from app.db.models import Farm


class Section(SoftDeletableMixin, Base):
    __tablename__ = "section"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]

    farm_id: Mapped[int] = mapped_column(ForeignKey("farm.id"))
    farm: Mapped["Farm"] = relationship("Farm", back_populates="sections")
