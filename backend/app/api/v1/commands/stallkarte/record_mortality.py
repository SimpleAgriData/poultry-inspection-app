import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app import domain
from app.api.v1.commands.stallkarte.setup import setup_stallkarte
from app.core import dependencies
from app.domain import StallkarteAggregator
from app.domain.stallkarte.events.dailyevents.mortality_recorded import (
    MortalityRecordedShift,
)
from app.services.database import Database
from app.shared.api import MessageResponse

router = APIRouter()
logger = logging.getLogger(__name__)


class RequestBody(BaseModel):
    stallkarte_id: int = Field(description="ID of the Stallkarte")
    production_day: int = Field(ge=0, description="Production day")
    section_number: int = Field(ge=0, description="Section number")
    shift: MortalityRecordedShift = Field(description="Shift (morning/evening)")
    natural_deaths: int | None = Field(description="Number of natural deaths")
    selective_deaths: int | None = Field(description="Number of selective deaths")


@router.post(
    "/record-mortality",
    response_model=MessageResponse,
    name="Record Mortality",
    description="Record mortality data",
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

    events = stallkarte.record_mortality(
        production_day=request_body.production_day,
        section_number=request_body.section_number,
        natural_deaths=request_body.natural_deaths,
        selective_deaths=request_body.selective_deaths,
        shift=request_body.shift,
    )

    for event in events:
        db.stallkarte_repository.add_event(stallkarte.id, event)

    StallkarteAggregator.apply_to(stallkarte, holding.farms, events)

    logger.info(
        f"Mortality recorded for section '{request_body.section_number}' "
        f"on production day '{request_body.production_day}' "
        f"during shift '{request_body.shift}'"
        f"for Stallkarte ID '{stallkarte.id}'"
    )

    return MessageResponse(
        message=f"Mortality recorded successfully for "
        f"section '{request_body.section_number}' on "
        f"production day '{request_body.production_day}' "
        f"during shift '{request_body.shift}'"
    )
