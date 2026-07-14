import logging
from enum import StrEnum, auto

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app import domain
from app.core import dependencies
from app.services.database import Database

router = APIRouter()
logger = logging.getLogger(__name__)


class ResponseBodySection(BaseModel):
    id: int
    name: str


class ResponseBodyFarmType(StrEnum):
    REARING = auto()
    FATTENING = auto()
    COMBINED = auto()


class ResponseBodyFarm(BaseModel):
    id: int
    type: ResponseBodyFarmType
    name: str
    vvvo_number: str

    sections: list[ResponseBodySection]


class ResponseBodyHolding(BaseModel):
    id: int
    owner_user_id: str
    name: str
    hatchery: str
    eco_control_number: str
    breed: str
    address_street: str
    address_zip: str
    address_city: str
    farms: list[ResponseBodyFarm]


class ResponseBody(BaseModel):
    holding: ResponseBodyHolding | None


def _translate_section(db_section: domain.Section) -> ResponseBodySection:
    return ResponseBodySection(
        id=db_section.id,
        name=db_section.name,
    )


def _translate_farm(db_farm: domain.Farm) -> ResponseBodyFarm:
    return ResponseBodyFarm(
        id=db_farm.id,
        type=ResponseBodyFarmType(db_farm.type.value),
        name=db_farm.name,
        sections=[_translate_section(section) for section in db_farm.sections],
        vvvo_number=db_farm.vvvo_number,
    )


def _translate_holding(db_holding: domain.AgriculturalHolding) -> ResponseBodyHolding:
    return ResponseBodyHolding(
        id=db_holding.id,
        owner_user_id=db_holding.owner_user_id,
        name=db_holding.name,
        farms=[_translate_farm(farm) for farm in db_holding.farms],
        hatchery=db_holding.hatchery,
        eco_control_number=db_holding.eco_control_number,
        breed=db_holding.breed,
        address_street=db_holding.address_street,
        address_zip=db_holding.address_zip,
        address_city=db_holding.address_city,
    )


@router.get(
    "/find-my-agricultural-holding",
    response_model=ResponseBody,
    name="Find The Agricultural Holding of the Authenticated User",
    description="Retrieve the agricultural holding associated with the "
    "authenticated user",
    tags=["Agricultural Holding", "User"],
    responses={
        401: {"description": "Authentication required or invalid token"},
        422: {"description": "Request validation error"},
    },
)
def handler(
    user: domain.User = Depends(dependencies.authenticate),
    db: Database = Depends(dependencies.database),
) -> ResponseBody:
    holding = db.agricultural_holding_repository.get_holding_by_owner(user.id)

    if holding is None:
        logger.warning(
            f"User '{user.username}' attempted to find agricultural holding, "
            "but none was found"
        )
        return ResponseBody(holding=None)

    response_holding = _translate_holding(holding)
    return ResponseBody(holding=response_holding)
