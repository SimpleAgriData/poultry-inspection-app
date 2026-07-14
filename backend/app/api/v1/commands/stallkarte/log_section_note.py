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
    section_number: int = Field(ge=0, description="Section number")
    note: str = Field(description="Section note content")


@router.post(
    "/log-section-note",
    response_model=MessageResponse,
    name="Log Section Note",
    description="Log a note for a specific section",
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

    events = stallkarte.log_section_note(
        production_day=request_body.production_day,
        section_number=request_body.section_number,
        note=request_body.note,
    )

    for event in events:
        db.stallkarte_repository.add_event(stallkarte.id, event)

    StallkarteAggregator.apply_to(stallkarte, holding.farms, events)

    logger.info(
        f"Note for section '{request_body.section_number}' logged for "
        f"Stallkarte ID '{stallkarte.id}'"
    )

    return MessageResponse(
        message=f"Section note logged successfully for "
        f"section '{request_body.section_number}'"
    )
