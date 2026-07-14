import datetime
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
    stallkarte_id: int = Field(description="ID of the Stallkarte to revise")
    date_hatched: datetime.date = Field(description="The revised hatch date")
    hatchery_name: str = Field(description="The revised name of the hatchery")
    breed: str = Field(description="The revised breed of the animals")
    fattening_cycle: str = Field(
        min_length=1, description="The revised fattening cycle identifier"
    )
    is_eu_bio: bool = Field(description="Indicates if the production is EU organic")
    is_naturland: bool = Field(
        description="Indicates if the production is Naturland certified"
    )


@router.post(
    "/revise-details",
    response_model=MessageResponse,
    name="Revise Stallkarte details",
    description="Revise the details of an existing Stallkarte, such as hatch date, "
    "breed, or fattening cycle",
    responses={
        400: {"description": "Bad request"},
        401: {"description": "Authentication required or invalid token"},
        403: {"description": "Permission denied to revise this Stallkarte"},
        422: {"description": "Request body validation error"},
    },
)
def handler(
    request_body: RequestBody,
    user: domain.User = Depends(dependencies.authenticate),
    db: Database = Depends(dependencies.database),
) -> MessageResponse:
    stallkarte, holding = setup_stallkarte(db, user.id, request_body.stallkarte_id)

    events = stallkarte.revise_details(
        date_hatched=request_body.date_hatched,
        hatchery_name=request_body.hatchery_name,
        breed=request_body.breed,
        fattening_cycle=request_body.fattening_cycle,
        is_eu_bio=request_body.is_eu_bio,
        is_naturland=request_body.is_naturland,
    )

    for event in events:
        db.stallkarte_repository.add_event(stallkarte.id, event)

    StallkarteAggregator.apply_to(stallkarte, holding.farms, events)

    logger.info(f"Stallkarte ID '{stallkarte.id}' revised by user '{user.username}'")

    return MessageResponse(message="Stallkarte details revised successfully")
