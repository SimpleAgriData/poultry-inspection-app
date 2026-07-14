import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app import domain
from app.api.v1.commands.stallkarte.setup import setup_stallkarte
from app.core import dependencies
from app.domain import StallkarteAggregator
from app.domain.stallkarte.events.models import WeatherCondition
from app.services.database import Database
from app.shared.api import MessageResponse

router = APIRouter()
logger = logging.getLogger(__name__)


class RequestBody(BaseModel):
    stallkarte_id: int = Field(description="ID of the Stallkarte")
    production_day: int = Field(ge=0, description="Production day")
    opening_time: str | None = Field(description="Opening time as HH:MM")
    weather_conditions: list[WeatherCondition] = Field(
        description="Selected weather conditions"
    )
    veterinarian: bool = Field(description="Whether veterinarian was present")


@router.post(
    "/record-fattening-day-data",
    response_model=MessageResponse,
    name="Record Fattening Day Data",
    description="Record additional fattening day data",
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

    events = stallkarte.record_fattening_day_data(
        production_day=request_body.production_day,
        opening_time=request_body.opening_time,
        weather_conditions=request_body.weather_conditions,
        veterinarian=request_body.veterinarian,
    )

    for event in events:
        db.stallkarte_repository.add_event(stallkarte.id, event)

    StallkarteAggregator.apply_to(stallkarte, holding.farms, events)

    logger.info(
        f"Fattening day data recorded on production day "
        f"'{request_body.production_day}' for Stallkarte ID '{stallkarte.id}'"
    )

    return MessageResponse(
        message=(
            "Fattening day data recorded successfully on "
            f"production day '{request_body.production_day}'"
        )
    )
