import datetime
import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app import domain
from app.api.v1.commands.stallkarte.setup import setup_stallkarte
from app.core import dependencies
from app.domain import StallkarteAggregator, StallkarteCycle
from app.services.database import Database
from app.shared.api import MessageResponse

router = APIRouter()
logger = logging.getLogger(__name__)


class RequestBody(BaseModel):
    stallkarte_id: int = Field(description="ID of the Stallkarte")
    cycle: StallkarteCycle = Field(
        description="Checklist cycle ('rearing' or 'fattening')"
    )
    date: datetime.date | None = Field(description="Date of silo cleaning")
    detergent: str | None = Field(description="Type of detergent used for cleaning")
    dosis: str | None = Field(description="Dosage of detergent used for cleaning")


@router.post(
    "/clean-silo",
    response_model=MessageResponse,
    name="Clean Silo",
    description="Record silo cleaning for the Stallkarte in a checklist cycle",
    tags=["Stallkarte Checklist"],
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

    events = stallkarte.clean_silo(
        cycle=request_body.cycle,
        date=request_body.date,
        detergent=request_body.detergent,
        dosis=request_body.dosis,
    )

    for event in events:
        db.stallkarte_repository.add_event(stallkarte.id, event)

    StallkarteAggregator.apply_to(stallkarte, holding.farms, events)

    logger.info(
        f"Recorded silo cleaning for Stallkarte ID '{stallkarte.id}' in cycle "
        f"'{request_body.cycle}' with detergent '{request_body.detergent}' and dosis "
        f"'{request_body.dosis}' on date '{request_body.date}'"
    )

    return MessageResponse(
        message=f"Silo cleaning completed successfully for cycle '{request_body.cycle}'"
    )
