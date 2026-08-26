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
    production_day: int = Field(ge=0, description="Production day")
    general_notes: list["RequestBodyGeneralNoteEntry"] = Field(
        default_factory=list,
        description="Complete list of general notes for the production day",
    )


type ApiGeneralNoteType = Literal[
    "vaccination",
    "treatment",
    "feeding",
    "relocation",
    "sock_test",
    "other",
]
type ApiVaccinationCode = Literal["nd", "gumboro", "ib", "kokzidien"]
type ApiTreatmentCode = Literal[
    "amproline",
    "pyanosid",
    "lincospectin",
    "phenoxypen_wsp",
    "baytril",
    "lanflox",
    "amoxicillin",
    "aviapen",
    "baycox",
    "biocillin",
    "dozuril",
    "enro_sleecol",
    "enroxal",
    "neomycinsulfat",
    "octacillin",
    "parofor",
    "pharmasin",
    "rhemox_forte",
    "solomocta",
    "t_s_sol",
    "toltra_k",
]
type ApiTreatmentAmountUnit = Literal["l/1000", "g/1000", "ml", "mg", "l", "kg"]
type ApiWaitingTimeUnit = Literal["day", "week"]
type ApiSockTestResult = Literal["positive", "negative"]


class RequestBodyGeneralNoteEntry(BaseModel):
    id: str
    note_type: ApiGeneralNoteType
    note_text: str | None = None
    delivery_receipt_number: str | None = None
    batch_number: str | None = None
    vaccination_code: ApiVaccinationCode | None = None
    treatment_code: ApiTreatmentCode | None = None
    treatment_amount_value: float | None = None
    treatment_amount_unit: ApiTreatmentAmountUnit | None = None
    treatment_waiting_time_value: int | None = Field(default=None, ge=0)
    treatment_waiting_time_unit: ApiWaitingTimeUnit | None = None
    sock_test_result: ApiSockTestResult | None = None
    slaughter_animals_count: int | None = Field(default=None, ge=0)


@router.post(
    "/save-general-notes",
    response_model=MessageResponse,
    name="Save General Notes",
    description="Replace all general notes for a production day",
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

    general_notes = [
        models.NoteEntry(
            id=note.id,
            note_type=models.NoteType(note.note_type),
            note_text=note.note_text,
            delivery_receipt_number=note.delivery_receipt_number,
            batch_number=note.batch_number,
            vaccination_code=(
                models.VaccinationCode(note.vaccination_code)
                if note.vaccination_code is not None
                else None
            ),
            treatment_code=(
                models.TreatmentCode(note.treatment_code)
                if note.treatment_code is not None
                else None
            ),
            treatment_amount_value=note.treatment_amount_value,
            treatment_amount_unit=(
                models.TreatmentAmountUnit(note.treatment_amount_unit)
                if note.treatment_amount_unit is not None
                else None
            ),
            treatment_waiting_time_value=note.treatment_waiting_time_value,
            treatment_waiting_time_unit=(
                models.WaitingTimeUnit(note.treatment_waiting_time_unit)
                if note.treatment_waiting_time_unit is not None
                else None
            ),
            sock_test_result=(
                models.SockTestResult(note.sock_test_result)
                if note.sock_test_result is not None
                else None
            ),
            slaughter_animals_count=note.slaughter_animals_count,
        )
        for note in request_body.general_notes
    ]

    events = stallkarte.save_general_notes(
        production_day=request_body.production_day,
        general_notes=general_notes,
    )

    for event in events:
        db.stallkarte_repository.add_event(stallkarte.id, event)

    StallkarteAggregator.apply_to(stallkarte, holding.farms, events)

    logger.info(f"General notes saved for Stallkarte ID '{stallkarte.id}'")

    return MessageResponse(message="General notes saved successfully")
