from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from app.domain import Farm


class Section(BaseModel):
    id: int
    name: str
    farm: "Farm"
