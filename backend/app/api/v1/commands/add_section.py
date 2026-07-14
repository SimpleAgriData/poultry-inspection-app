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
    name: str = Field(min_length=1, description="Name of the section")
    farm_id: int = Field(
        gt=0, description="ID of the farm to which the section will be added"
    )


class ResponseBody(BaseModel):
    message: str


@router.post(
    "/add-section",
    response_model=ResponseBody,
    name="Add Section",
    description="Add a new section to an existing barn",
    tags=["Section", "Farm"],
    responses={
        401: {"description": "Authentication required or invalid token"},
        403: {"description": "Permission denied to add a section to the barn"},
        404: {"description": "Farm not found"},
        422: {"description": "Request body validation error"},
    },
)
def handler(
    request_body: RequestBody,
    user: domain.User = Depends(dependencies.authenticate),
    db: Database = Depends(dependencies.database),
) -> ResponseBody:
    farm = db.farm_repository.get_farm_by_id(request_body.farm_id)
    if farm is None:
        raise HTTPException(
            404,
            f"Farm ID '{request_body.farm_id}' not found",
        )
    holding = farm.holding
    if holding.owner_user_id != user.id:
        raise HTTPException(
            403,
            f"Missing permission to add Section to Farm ID '{request_body.farm_id}'",
        )

    section_candidate = database.SectionCandidate(
        name=request_body.name,
    )

    section = db.section_repository.add_section(request_body.farm_id, section_candidate)

    logger.info(
        f"Section '{section.name}' ({section.id}) added to Farm "
        f"'{farm.name}' ({farm.id}) by user '{user.username}'"
    )

    return ResponseBody(message=f"Section '{section.name}' added successfully")
