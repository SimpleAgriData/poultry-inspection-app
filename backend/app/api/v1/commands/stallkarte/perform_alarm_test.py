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
    did_emergency_power_test: bool | None = Field(
        description="Whether an emergency power test was performed"
    )
    did_alarm_test: bool | None = Field(
        description="Whether an alarm test was performed"
    )


@router.post(
    "/perform-alarm-test",
    response_model=MessageResponse,
    name="Perform Alarm Test",
    description="Record the performance of an alarm test for the Stallkarte in a "
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

    events = stallkarte.perform_alarm_test(
        cycle=request_body.cycle,
        did_emergency_power_test=request_body.did_emergency_power_test,
        did_alarm_test=request_body.did_alarm_test,
    )

    for event in events:
        db.stallkarte_repository.add_event(stallkarte.id, event)

    StallkarteAggregator.apply_to(stallkarte, holding.farms, events)

    logger.info(
        f"User '{user.username}' performed alarm test for "
        f"Stallkarte ID {stallkarte.id} in cycle '{request_body.cycle}'"
    )

    return MessageResponse(
        message=f"Alarm test performed successfully for cycle '{request_body.cycle}'"
    )
