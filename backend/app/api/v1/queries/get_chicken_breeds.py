import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app import domain
from app.core import dependencies
from app.services.database import Database

router = APIRouter()
logger = logging.getLogger(__name__)


class ResponseBody(BaseModel):
    breeds: list[str]


@router.get(
    "/chicken-breeds",
    response_model=ResponseBody,
    name="Find chicken breeds",
    description="Retrieve a list of chicken breeds for the authenticated user",
    tags=["Breeds", "User"],
    responses={
        401: {"description": "Authentication required or invalid token"},
        403: {"description": "Permission denied to access breeds"},
        422: {"description": "Request validation error"},
    },
)
def handler(
    user: domain.User = Depends(dependencies.authenticate),
    db: Database = Depends(dependencies.database),
) -> ResponseBody:
    
    chicken_breeds = db.chicken_breed_repository.get_all_breeds()
    breeds = [breed.label for breed in chicken_breeds]
    return ResponseBody(breeds=breeds)
