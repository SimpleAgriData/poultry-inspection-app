import logging

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


class RequestBodyParentFlockEntry(BaseModel):
    herd_identifier: str = Field(min_length=1)
    production_week: int = Field(gt=0)


class RequestBodySectionInstallationDetails(BaseModel):
    section_number: int = Field(ge=1)
    initial_animals_count: int = Field(gt=0)
    initial_weight_grams: float = Field(gt=0)
    bedding: str = Field(min_length=1)
    parent_flocks: list[RequestBodyParentFlockEntry] = Field(min_length=1)


class RequestBody(BaseModel):
    stallkarte_id: int
    section_details: list[RequestBodySectionInstallationDetails]


@router.post(
    "/replace-installation-details",
    response_model=MessageResponse,
    name="Replace Installation Details",
    description="Replace installation details for all sections",
)
def handler(
    request_body: RequestBody,
    user: domain.User = Depends(dependencies.authenticate),
    db: Database = Depends(dependencies.database),
) -> MessageResponse:
    stallkarte, holding = setup_stallkarte(db, user.id, request_body.stallkarte_id)

    section_details = [
        models.SectionInstallationDetails(
            section_number=section.section_number,
            initial_animals_count=section.initial_animals_count,
            initial_weight_grams=section.initial_weight_grams,
            bedding=section.bedding,
            parent_flocks=[
                models.ParentFlockEntry(
                    herd_identifier=parent_flock.herd_identifier,
                    production_week=parent_flock.production_week,
                )
                for parent_flock in section.parent_flocks
            ],
        )
        for section in request_body.section_details
    ]

    events = stallkarte.replace_installation_details(section_details=section_details)

    for event in events:
        db.stallkarte_repository.add_event(stallkarte.id, event)

    StallkarteAggregator.apply_to(stallkarte, holding.farms, events)

    logger.info(f"Installation details replaced for Stallkarte ID '{stallkarte.id}'")

    return MessageResponse(message="Installation details replaced successfully")
