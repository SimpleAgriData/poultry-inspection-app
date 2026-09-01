from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.mixins import Base




class ChickenBreed(Base):
    __tablename__ = "chicken_breed"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    label: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str]

