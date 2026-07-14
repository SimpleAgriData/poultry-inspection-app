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
    stallkarte_id: int = Field(description="ID of the Stallkarte")
    transfer_date: datetime.date = Field(description="Date of the flock transfer")
    animals_by_section_number: dict[int, int] = Field(
        description="Mapping of section number to number of animals transferred"
    )


@router.post(
    "/transfer-flock",
    response_model=MessageResponse,
    name="Transfers flock to fattening farm",
    description="Start the fattening phase",
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

    events = stallkarte.transfer_flock(
        transfer_date=request_body.transfer_date,
        animals_by_section_number=request_body.animals_by_section_number,
    )

    for event in events:
        db.stallkarte_repository.add_event(stallkarte.id, event)

    StallkarteAggregator.apply_to(stallkarte, holding.farms, events)

    logger.info(f"Flock transferred for Stallkarte ID '{stallkarte.id}'")

    return MessageResponse(message="Flock transferred successfully")
