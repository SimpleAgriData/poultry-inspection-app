import datetime
import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app import domain
from app.core import dependencies
from app.services.database import Database

router = APIRouter()
logger = logging.getLogger(__name__)


class ShallowStallkarte(BaseModel):
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
    def from_domain(cls, stallkarte: domain.ShallowStallkarte) -> "ShallowStallkarte":
        return cls(
            id=stallkarte.id,
            holding_id=stallkarte.holding_id,
            date_started=stallkarte.date_started,
            date_hatched=stallkarte.date_hatched,
            hatchery_name=stallkarte.hatchery_name,
            breed=stallkarte.breed,
            fattening_cycle=stallkarte.fattening_cycle,
            eco_control_number=stallkarte.eco_control_number,
            is_eu_bio=stallkarte.is_eu_bio,
            is_naturland=stallkarte.is_naturland,
            is_finished=stallkarte.is_finished,
            date_finished=stallkarte.date_finished,
        )


class ResponseBody(BaseModel):
    active_stallkarten: list[ShallowStallkarte]
    archived_stallkarten: list[ShallowStallkarte]


@router.get(
    "/find-my-stallkarten",
    response_model=ResponseBody,
    name="Find My Stallkarten",
    description="Retrieve all Stallkarten associated with the authenticated user's "
    "agricultural holding, categorized into active and archived Stallkarten",
    tags=["Stallkarte", "User"],
    responses={
        401: {"description": "Authentication required or invalid token"},
        403: {"description": "Permission denied to access Stallkarten"},
        422: {"description": "Request validation error"},
    },
)
def handler(
    user: domain.User = Depends(dependencies.authenticate),
    db: Database = Depends(dependencies.database),
) -> ResponseBody:
    holding = db.agricultural_holding_repository.get_holding_by_owner(user.id)

    if holding is None:
        logger.warning(
            f"User '{user.username}' has no agricultural holding "
            f"to retrieve Stallkarten for"
        )
        return ResponseBody(active_stallkarten=[], archived_stallkarten=[])

    stallkarten = db.stallkarte_repository.get_shallow_stallkarten_by_holding_id(
        holding.id
    )

    logger.info(
        f"Retrieved {len(stallkarten)} Stallkarte(n) for user '{user.username}'"
    )

    stallkarten.sort(key=lambda s: s.date_started, reverse=True)

    active_stallkarten: list[ShallowStallkarte] = []
    archived_stallkarten: list[ShallowStallkarte] = []

    for stallkarte in stallkarten:
        shallow_stallkarte = ShallowStallkarte.from_domain(stallkarte)
        if shallow_stallkarte.is_finished:
            archived_stallkarten.append(shallow_stallkarte)
        else:
            active_stallkarten.append(shallow_stallkarte)

    return ResponseBody(
        active_stallkarten=active_stallkarten,
        archived_stallkarten=archived_stallkarten,
    )
