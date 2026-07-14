import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app import domain
from app.core import dependencies
from app.services.database import Database

router = APIRouter()
logger = logging.getLogger(__name__)


class RequestBody(BaseModel):
    section_id: int = Field(gt=0, description="ID of the section to delete")


class ResponseBody(BaseModel):
    message: str


@router.post(
    "/delete-section",
    response_model=ResponseBody,
    name="Delete Section",
    description="Delete a section owned by the authenticated user",
    tags=["Section", "Farm"],
    responses={
        401: {"description": "Authentication required or invalid token"},
        403: {"description": "Permission denied to delete the section"},
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
            403, f"missing permission to delete Section ID '{request_body.section_id}'"
        )

    db.section_repository.delete_section(request_body.section_id)

    logger.info(
        f"Section '{section.name}' ({section.id}) deleted by user '{user.username}'"
    )

    return ResponseBody(message=f"Section '{section.name}' deleted successfully")
