import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app import domain
from app.api.v1.commands.stallkarte.setup import setup_stallkarte
from app.core import dependencies
from app.domain import StallkarteAggregator
from app.services.database import Database
from app.shared.api import MessageResponse

router = APIRouter()
logger = logging.getLogger(__name__)


class RequestBody(BaseModel):
    stallkarte_id: int = Field(description="ID of the Stallkarte")
    production_day: int = Field(ge=0, description="Production day")
    amount_liters: float = Field(description="Amount of water consumed in liters")


@router.post(
    "/record-water-consumption",
    response_model=MessageResponse,
    name="Record Water Consumption",
    description="Record water consumption data",
    tags=["Stallkarte Daily Events"],
    responses={
        400: {"description": "Bad request"},
        401: {"description": "Authentication required or invalid token"},
        403: {"description": "Permission denied"},
        404: {"description": "Stallkarte not found"},
        422: {"description": "Request body validation error"},
    },
)
def handler(
    request_body: RequestBody,
    user: domain.User = Depends(dependencies.authenticate),
    db: Database = Depends(dependencies.database),
) -> MessageResponse:
    stallkarte, holding = setup_stallkarte(db, user.id, request_body.stallkarte_id)

    events = stallkarte.record_water_consumption(
        production_day=request_body.production_day,
        amount_liters=request_body.amount_liters,
    )

    for event in events:
        db.stallkarte_repository.add_event(stallkarte.id, event)

    StallkarteAggregator.apply_to(stallkarte, holding.farms, events)

    logger.info(
        f"Water consumption recorded on production day '{request_body.production_day}' "
        f"for Stallkarte ID '{stallkarte.id}'"
    )

    return MessageResponse(
        message=f"Water consumption recorded successfully on "
        f"production day '{request_body.production_day}'"
    )
