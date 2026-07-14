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
    name: str = Field(min_length=1, description="Name of the farm")
    type: RequestBodyFarmType = Field(description="Type of the farm")
    vvvo_number: str = Field(min_length=1, description="VVVO number")
    agricultural_holding_id: int = Field(
        gt=0,
        description="ID of the agricultural holding to which the farm will be added",
    )


class ResponseBody(BaseModel):
    message: str


@router.post(
    "/add-farm",
    response_model=ResponseBody,
    name="Add Farm",
    description="Add a new farm to an existing agricultural holding",
    tags=["Farm", "Agricultural Holding"],
    responses={
        401: {"description": "Authentication required or invalid token"},
        403: {"description": "Permission denied to add a farm to the holding"},
        404: {"description": "Agricultural holding not found"},
        422: {"description": "Request body validation error"},
    },
)
def handler(
    request_body: RequestBody,
    user: domain.User = Depends(dependencies.authenticate),
    db: Database = Depends(dependencies.database),
) -> ResponseBody:
    holding = db.agricultural_holding_repository.get_holding_by_id(
        request_body.agricultural_holding_id
    )
    if holding is None:
        raise HTTPException(
            404,
            f"Agricultural Holding ID '{request_body.agricultural_holding_id}' "
            f"not found",
        )
    if holding.owner_user_id != user.id:
        raise HTTPException(
            403,
            f"Missing permission to add Farm to Agricultural Holding ID "
            f"'{request_body.agricultural_holding_id}'",
        )

    farm_candidate = database.FarmCandidate(
        name=request_body.name,
        type=database.FarmTypeCandidate(request_body.type.value),
        vvvo_number=request_body.vvvo_number,
    )

    farm = db.farm_repository.add_farm(
        request_body.agricultural_holding_id, farm_candidate
    )

    logger.info(
        f"Farm '{farm.name}' ({farm.id}) of type '{farm.type.name}' "
        f"with VVVO number '{farm.vvvo_number}' "
        f"added to Agricultural Holding ID '{request_body.agricultural_holding_id}'"
    )

    return ResponseBody(message=f"Farm '{farm.name}' added successfully")
