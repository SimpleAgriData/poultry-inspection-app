import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app import domain
from app.core import dependencies
from app.domain import StallkarteAggregator
from app.services.database import Database

router = APIRouter()
logger = logging.getLogger(__name__)


class RequestBody(BaseModel):
    date_started: datetime.date = Field(description="Start date of the Stallkarte")
    date_hatched: datetime.date = Field(description="Hatch date")
    hatchery_name: str = Field(description="Name of the hatchery")
    breed: str = Field(description="Breed of the animals")
    fattening_cycle: str = Field(min_length=1, description="Fattening cycle identifier")
    eco_control_number: str = Field(description="Eco control number")
    is_eu_bio: bool = Field(description="Indicates if the production is EU organic")
    is_naturland: bool = Field(
        description="Indicates if the production is Naturland certified"
    )


class ResponseBody(BaseModel):
    message: str = Field(
        description="Response message indicating the result of the operation"
    )
    stallkarte_id: int = Field(description="ID of the newly created Stallkarte")


@router.post(
    "/start-stallkarte",
    response_model=ResponseBody,
    name="Start a new Stallkarte",
    description="Initialize a new Stallkarte with basic information",
    responses={
        400: {"description": "Bad request"},
        401: {"description": "Authentication required or invalid token"},
        403: {"description": "Permission denied to start a Stallkarte"},
        404: {"description": "Farm not found"},
        422: {"description": "Request body validation error"},
    },
)
def handler(
    request_body: RequestBody,
    user: domain.User = Depends(dependencies.authenticate),
    db: Database = Depends(dependencies.database),
) -> ResponseBody:
    holding = db.agricultural_holding_repository.get_holding_by_owner(user.id)
    if holding is None:
        raise HTTPException(400, "user has no associated agricultural holding")

    stallkarte = db.stallkarte_repository.create_stallkarte(holding.id)

    events = stallkarte.start_stallkarte(
        date_started=request_body.date_started,
        date_hatched=request_body.date_hatched,
        hatchery_name=request_body.hatchery_name,
        breed=request_body.breed,
        fattening_cycle=request_body.fattening_cycle,
        eco_control_number=request_body.eco_control_number,
        is_eu_bio=request_body.is_eu_bio,
        is_naturland=request_body.is_naturland,
    )

    for event in events:
        db.stallkarte_repository.add_event(stallkarte.id, event)

    StallkarteAggregator.apply_to(stallkarte, holding.farms, events)

    logger.info(f"Stallkarte ID '{stallkarte.id}' started by user '{user.username}'")

    return ResponseBody(
        message="Stallkarte started successfully", stallkarte_id=stallkarte.id
    )
