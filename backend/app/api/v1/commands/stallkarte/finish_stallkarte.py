import datetime
import logging
from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app import domain
from app.api.v1.commands.stallkarte.setup import setup_stallkarte
from app.core import dependencies
from app.domain import StallkarteAggregator
from app.domain.stallkarte.events import models
from app.services.database import Database
from app.shared.api import MessageResponse

router = APIRouter()
logger = logging.getLogger(__name__)


class RequestBody(BaseModel):
    stallkarte_id: int = Field(description="ID of the Stallkarte")
    date_finished: datetime.date = Field(
        description="Date when the Stallkarte was finished"
    )
    finish_notes: list["RequestBodyFinishNoteEntry"] = Field(
        default_factory=list,
        description="Structured finish notes for slaughter and catching",
    )


type ApiFinishNoteType = Literal["slaughter", "catching"]


class RequestBodyFinishNoteEntry(BaseModel):
    id: str
    note_type: ApiFinishNoteType
    slaughter_date: datetime.date | None = None
    slaughter_animals_count: int | None = Field(default=None, ge=0)
    slaughter_final_weight_kg: float | None = Field(default=None, ge=0)
    slaughterer_name: str | None = None
    catching_time: str | None = None
    catcher_name: str | None = None


@router.post(
    "/finish-stallkarte",
    response_model=MessageResponse,
    name="Finish Stallkarte",
    description="Finish a Stallkarte",
    responses={
        400: {"description": "Bad request"},
        401: {"description": "Authentication required or invalid token"},
        403: {"description": "Permission denied"},
        422: {"description": "Request body validation error"},
    },
)
def handler(
    request_body: RequestBody,
    user: domain.User = Depends(dependencies.authenticate),
    db: Database = Depends(dependencies.database),
) -> MessageResponse:
    stallkarte, holding = setup_stallkarte(db, user.id, request_body.stallkarte_id)

    finish_notes = [
        models.NoteEntry(
            id=note.id,
            note_type=models.NoteType(note.note_type),
            slaughter_date=note.slaughter_date,
            slaughter_animals_count=note.slaughter_animals_count,
            slaughter_final_weight_kg=note.slaughter_final_weight_kg,
            slaughterer_name=note.slaughterer_name,
            catching_time=note.catching_time,
            catcher_name=note.catcher_name,
        )
        for note in request_body.finish_notes
    ]

    events = stallkarte.finish(request_body.date_finished, finish_notes=finish_notes)

    for event in events:
        db.stallkarte_repository.add_event(stallkarte.id, event)

    db.stallkarte_repository.mark_finished(stallkarte.id)

    StallkarteAggregator.apply_to(stallkarte, holding.farms, events)

    logger.info(f"Stallkarte ID '{stallkarte.id}' finished")

    return MessageResponse(message="Stallkarte finished successfully")
