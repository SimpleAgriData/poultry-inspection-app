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
    did_perform_pest_control: bool | None = Field(
        description="Whether pest control measures were performed"
    )
    annotation: str | None = Field(
        description="Optional annotation for the pest control measures"
    )


@router.post(
    "/apply-pest-control-measures",
    response_model=MessageResponse,
    name="Apply Pest Control Measures",
    description="Apply pest control measures to the Stallkarte for a checklist cycle",
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

    events = stallkarte.apply_pest_control_measures(
        cycle=request_body.cycle,
        did_perform_pest_control=request_body.did_perform_pest_control,
        annotation=request_body.annotation,
    )

    for event in events:
        db.stallkarte_repository.add_event(stallkarte.id, event)

    StallkarteAggregator.apply_to(stallkarte, holding.farms, events)

    logger.info(
        f"Applied pest control measures for cycle '{request_body.cycle}' "
        f"on Stallkarte ID '{stallkarte.id}'"
    )

    return MessageResponse(
        message=f"Pest control measures applied for cycle '{request_body.cycle}'"
    )
