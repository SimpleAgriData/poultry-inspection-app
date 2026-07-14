from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from app.domain import Farm


class AgriculturalHolding(BaseModel):
    id: int
    owner_user_id: str
    name: str
    hatchery: str
    eco_control_number: str
    breed: str
    address_street: str
    address_zip: str
    address_city: str

    farms: list["Farm"]
