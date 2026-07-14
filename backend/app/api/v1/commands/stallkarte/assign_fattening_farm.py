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
    stallkarte_id: int = Field(description="ID of the Stallkarte")
    farm_id: int = Field(description="ID of the fattening farm")


@router.post(
    "/assign-fattening-farm",
    response_model=MessageResponse,
    name="Assign Fattening Farm",
    description="Assign a fattening farm to the Stallkarte",
    responses={
        400: {"description": "Bad request"},
        401: {"description": "Authentication required or invalid token"},
        403: {"description": "Permission denied"},
        404: {"description": "Stallkarte or Farm not found"},
        422: {"description": "Request body validation error"},
    },
)
def handler(
    request_body: RequestBody,
    user: domain.User = Depends(dependencies.authenticate),
    db: Database = Depends(dependencies.database),
) -> MessageResponse:
    stallkarte, holding = setup_stallkarte(db, user.id, request_body.stallkarte_id)

    farm = next((f for f in holding.farms if f.id == request_body.farm_id), None)
    if farm is None:
        raise HTTPException(
            404, f"Farm ID '{request_body.farm_id}' not found in holding"
        )

    events = stallkarte.assign_fattening_farm(farm)

    for event in events:
        db.stallkarte_repository.add_event(stallkarte.id, event)

    StallkarteAggregator.apply_to(stallkarte, holding.farms, events)

    logger.info(
        f"Assigned fattening farm '{farm.id}' to Stallkarte ID '{stallkarte.id}'"
    )

    return MessageResponse(message=f"Fattening farm '{farm.id}' assigned successfully")
