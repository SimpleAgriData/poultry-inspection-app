import logging

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel, Field

from app import domain
from app.core import dependencies
from app.services import database
from app.services.database import Database

router = APIRouter()
logger = logging.getLogger(__name__)


class RequestBody(BaseModel):
    holding_id: int = Field(
        gt=0, description="ID of the agricultural holding to update"
    )
    name: str = Field(
        min_length=1, description="Updated name of the agricultural holding"
    )
    hatchery: str = Field(min_length=1, description="Updated hatchery")
    eco_control_number: str = Field(
        min_length=1, description="Updated eco control number"
    )
    breed: str = Field(min_length=1, description="Updated breed of chickens")
    address_street: str = Field(min_length=1, description="Updated street address")
    address_zip: str = Field(min_length=1, description="Updated ZIP code")
    address_city: str = Field(min_length=1, description="Updated city")


class ResponseBody(BaseModel):
    message: str = Field(description="Confirmation message")


@router.post(
    "/update-agricultural-holding",
    response_model=ResponseBody,
    name="Update Agricultural Holding",
    description="Update an agricultural holding owned by the authenticated user",
    tags=["Agricultural Holding"],
    responses={
        401: {"description": "Authentication required or invalid token"},
        403: {"description": "Permission denied to update the holding"},
        404: {"description": "Agricultural holding not found"},
        422: {"description": "Request body validation error"},
    },
)
def handler(
    request: RequestBody = Body(title="UpdateAgriculturalHoldingRequest"),
    user: domain.User = Depends(dependencies.authenticate),
    db: Database = Depends(dependencies.database),
) -> ResponseBody:
    holding = db.agricultural_holding_repository.get_holding_by_id(request.holding_id)
    if holding is None:
        raise HTTPException(
            404, f"Agricultural Holding ID '{request.holding_id}' not found"
        )
    if holding.owner_user_id != user.id:
        raise HTTPException(
            403,
            (
                "Missing permission to update Agricultural Holding ID "
                f"'{request.holding_id}'"
            ),
        )

    candidate = database.AgriculturalHoldingCandidate(
        owner_user_id=user.id,
        name=request.name,
        hatchery=request.hatchery,
        eco_control_number=request.eco_control_number,
        breed=request.breed,
        address_street=request.address_street,
        address_zip=request.address_zip,
        address_city=request.address_city,
    )

    updated = db.agricultural_holding_repository.update_holding(
        request.holding_id, candidate
    )

    logger.info(
        f"Agricultural Holding '{updated.name}' ({updated.id}) "
        f"updated by user '{user.username}'"
    )

    return ResponseBody(
        message=f"Agricultural Holding '{updated.name}' updated successfully"
    )
