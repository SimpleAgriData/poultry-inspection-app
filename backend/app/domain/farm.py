from enum import StrEnum
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from app.domain import AgriculturalHolding, Section


class FarmType(StrEnum):
    FATTENING = "fattening"
    REARING = "rearing"
    COMBINED = "combined"


class Farm(BaseModel):
    id: int
    type: FarmType
    name: str
    vvvo_number: str

    holding: "AgriculturalHolding"
    sections: list["Section"]
