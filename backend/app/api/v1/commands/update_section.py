import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app import domain
from app.core import dependencies
from app.services import database
from app.services.database import Database

router = APIRouter()
logger = logging.getLogger(__name__)


class RequestBody(BaseModel):
    section_id: int = Field(gt=0, description="ID of the section to update")
    name: str = Field(min_length=1, description="Updated name of the section")


class ResponseBody(BaseModel):
    message: str


@router.post(
    "/update-section",
    response_model=ResponseBody,
    name="Update Section",
    description="Update a section owned by the authenticated user",
    tags=["Section", "Farm"],
    responses={
        401: {"description": "Authentication required or invalid token"},
        403: {"description": "Permission denied to update the section"},
        404: {"description": "Section not found"},
        422: {"description": "Request body validation error"},
    },
)
def handler(
    request_body: RequestBody,
    user: domain.User = Depends(dependencies.authenticate),
    db: Database = Depends(dependencies.database),
) -> ResponseBody:
    section = db.section_repository.get_section_by_id(request_body.section_id)
    if section is None:
        raise HTTPException(404, f"section ID '{request_body.section_id}' not found")
    if section.farm.holding.owner_user_id != user.id:
        raise HTTPException(
            403, f"missing permission to update Section ID '{request_body.section_id}'"
        )

    candidate = database.SectionCandidate(
        name=request_body.name,
    )

    updated = db.section_repository.update_section(request_body.section_id, candidate)

    logger.info(
        f"Section '{updated.name}' ({updated.id}) updated by user '{user.username}'"
    )

    return ResponseBody(message=f"Section '{updated.name}' updated successfully")
