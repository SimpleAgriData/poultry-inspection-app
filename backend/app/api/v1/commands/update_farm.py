import logging
from enum import StrEnum, auto

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app import domain
from app.core import dependencies
from app.services import database
from app.services.database import Database

router = APIRouter()
logger = logging.getLogger(__name__)


class RequestBodyFarmType(StrEnum):
    FATTENING = auto()
    REARING = auto()
    COMBINED = auto()


class RequestBody(BaseModel):
    farm_id: int = Field(gt=0, description="ID of the farm to update")
    name: str = Field(min_length=1, description="Updated name of the farm")
    type: RequestBodyFarmType = Field(description="Updated type of the farm")
    vvvo_number: str = Field(min_length=1, description="VVVO number")


class ResponseBody(BaseModel):
    message: str


@router.post(
    "/update-farm",
    response_model=ResponseBody,
    name="Update Farm",
    description=(
        "Update a farm belonging to one of the authenticated user's agricultural "
        "holdings"
    ),
    tags=["Farm", "Agricultural Holding"],
    responses={
        401: {"description": "Authentication required or invalid token"},
        403: {"description": "Permission denied to update the farm"},
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
        raise HTTPException(404, f"farm ID '{request_body.farm_id}' not found")
    if farm.holding.owner_user_id != user.id:
        raise HTTPException(
            403, f"missing permission to update Farm ID '{request_body.farm_id}'"
        )

    candidate = database.FarmCandidate(
        name=request_body.name,
        type=database.FarmTypeCandidate(request_body.type.value),
        vvvo_number=request_body.vvvo_number,
    )

    updated = db.farm_repository.update_farm(request_body.farm_id, candidate)

    logger.info(
        f"Farm '{updated.name}' ({updated.id}) "
        f"updated to type '{updated.type.name}' "
        f"with VVVO number '{updated.vvvo_number}' "
        f"by user '{user.username}'"
    )

    return ResponseBody(message=f"Farm '{updated.name}' updated successfully")
