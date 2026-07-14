from enum import StrEnum, auto

from pydantic import BaseModel


class AssignedFarmType(StrEnum):
    FATTENING = auto()
    REARING = auto()
    COMBINED = auto()


class AssignedFarmSection(BaseModel):
    """
    Model for representing a section of an assigned farm of a fattening_farm_assigned
    or rearing_farm_assigned event.
    """

    id: int
    number: int
    name: str
