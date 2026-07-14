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
    name: str = Field(min_length=1, description="Name of the agricultural holding")
    hatchery: str = Field(
        min_length=1, description="Hatchery associated with the holding"
    )
    eco_control_number: str = Field(min_length=1, description="Eco control number")
    breed: str = Field(min_length=1, description="Breed of chickens")
    address_street: str = Field(
        min_length=1, description="Street address of the holding"
    )
    address_zip: str = Field(min_length=1, description="ZIP code of the holding")
    address_city: str = Field(min_length=1, description="City of the holding")


class ResponseBody(BaseModel):
    message: str = Field(description="Confirmation message")


@router.post(
    "/add-agricultural-holding",
    response_model=ResponseBody,
    name="Add Agricultural Holding",
    description="Add a new agricultural holding associated with the authenticated user",
    tags=["Agricultural Holding"],
    responses={
        400: {"description": "Bad request"},
        401: {"description": "Authentication required or invalid token"},
        422: {"description": "Request body validation error"},
    },
)
def handler(
    request: RequestBody = Body(
        title="AddAgriculturalHoldingRequest",
        description="Details of the agricultural holding to add",
    ),
    user: domain.User = Depends(dependencies.authenticate),
    db: Database = Depends(dependencies.database),
) -> ResponseBody:
    existing_holding = db.agricultural_holding_repository.get_holding_by_owner(user.id)
    if existing_holding is not None:
        raise HTTPException(400, "user already has an associated agricultural holding")

    holding_candidate = database.AgriculturalHoldingCandidate(
        owner_user_id=user.id,
        name=request.name,
        hatchery=request.hatchery,
        eco_control_number=request.eco_control_number,
        breed=request.breed,
        address_street=request.address_street,
        address_zip=request.address_zip,
        address_city=request.address_city,
    )

    holding = db.agricultural_holding_repository.add_holding(holding_candidate)

    logger.info(
        f"Agricultural Holding '{holding.name}' ({holding.id}) "
        f"added by user '{user.username}'"
    )

    return ResponseBody(
        message=f"Agricultural Holding '{holding.name}' added successfully"
    )
