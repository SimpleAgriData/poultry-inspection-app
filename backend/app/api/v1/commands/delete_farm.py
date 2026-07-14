import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app import domain
from app.core import dependencies
from app.services.database import Database

router = APIRouter()
logger = logging.getLogger(__name__)


class RequestBody(BaseModel):
    farm_id: int = Field(gt=0, description="ID of the farm to delete")


class ResponseBody(BaseModel):
    message: str


@router.post(
    "/delete-farm",
    response_model=ResponseBody,
    name="Delete Farm",
    description="Delete a farm owned by the authenticated user",
    tags=["Farm", "Agricultural Holding"],
    responses={
        401: {"description": "Authentication required or invalid token"},
        403: {"description": "Permission denied to delete the farm"},
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
            403, f"missing permission to delete Farm ID '{request_body.farm_id}'"
        )

    db.farm_repository.delete_farm(request_body.farm_id)

    logger.info(f"Farm '{farm.name}' ({farm.id}) deleted by user '{user.username}'")

    return ResponseBody(message=f"Farm '{farm.name}' deleted successfully")
