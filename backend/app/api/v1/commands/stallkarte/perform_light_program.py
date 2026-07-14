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
    did_dark_period_test: bool | None = Field(
        description="Whether a dark period test was performed"
    )
    had_divergence_due_to_vet: bool | None = Field(
        description="Whether there was a divergence due to veterinarian recommendation"
    )


@router.post(
    "/perform-light-program",
    response_model=MessageResponse,
    name="Perform Light Program",
    description="Record the performance of a light program for the Stallkarte in a "
    "checklist cycle",
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

    events = stallkarte.perform_lighting_program(
        cycle=request_body.cycle,
        did_dark_period_test=request_body.did_dark_period_test,
        had_divergence_due_to_vet=request_body.had_divergence_due_to_vet,
    )

    for event in events:
        db.stallkarte_repository.add_event(stallkarte.id, event)

    StallkarteAggregator.apply_to(stallkarte, holding.farms, events)

    logger.info(
        f"User '{user.username}' performed light program for "
        f"Stallkarte ID {stallkarte.id} in cycle '{request_body.cycle}' with dark "
        f"period test {request_body.did_dark_period_test} and divergence due to vet "
        f"{request_body.had_divergence_due_to_vet}"
    )

    return MessageResponse(
        message=f"Light program performed successfully for cycle '{request_body.cycle}'"
    )
