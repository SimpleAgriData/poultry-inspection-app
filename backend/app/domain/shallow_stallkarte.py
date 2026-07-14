import datetime

from pydantic import BaseModel


class ShallowStallkarte(BaseModel):
    """
    A shallow representation of a Stallkarte, containing only the most essential
    information needed for listing and identifying Stallkarten without the full details.
    """

    id: int
    holding_id: int
    date_started: datetime.date
    date_hatched: datetime.date
    hatchery_name: str
    breed: str
    fattening_cycle: str
    eco_control_number: str
    is_eu_bio: bool
    is_naturland: bool
    is_finished: bool
    date_finished: datetime.date | None

    @classmethod
    def default(
        cls, id: int, holding_id: int, is_finished: bool
    ) -> "ShallowStallkarte":
        return cls(
            id=id,
            holding_id=holding_id,
            date_started=datetime.date.min,
            date_hatched=datetime.date.min,
            hatchery_name="",
            breed="",
            fattening_cycle="",
            eco_control_number="",
            is_eu_bio=False,
            is_naturland=False,
            is_finished=is_finished,
            date_finished=None,
        )
