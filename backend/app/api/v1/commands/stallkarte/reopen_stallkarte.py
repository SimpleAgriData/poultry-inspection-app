import logging

from fastapi import APIRouter, Depends, HTTPException
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
    stallkarte_id: int = Field(gt=0, description="ID of the Stallkarte")


@router.post(
    "/reopen-stallkarte",
    response_model=MessageResponse,
    name="Reopen Stallkarte",
    description="Reopen a finished Stallkarte",
)
def handler(
    request_body: RequestBody,
    user: domain.User = Depends(dependencies.authenticate),
    db: Database = Depends(dependencies.database),
) -> MessageResponse:
    stallkarte, holding = setup_stallkarte(db, user.id, request_body.stallkarte_id)

    if not stallkarte.state.is_finished:
        raise HTTPException(400, "stallkarte is not finished")

    events = stallkarte.reopen()

    for event in events:
        db.stallkarte_repository.add_event(stallkarte.id, event)

    db.stallkarte_repository.mark_reopened(stallkarte.id)

    StallkarteAggregator.apply_to(stallkarte, holding.farms, events)

    logger.info(f"Stallkarte ID '{stallkarte.id}' reopened")

    return MessageResponse(message="Stallkarte reopened successfully")
