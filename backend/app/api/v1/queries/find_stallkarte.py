import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app import domain
from app.core import dependencies
from app.services.database import Database
from app.shared.api import ResponseBodyStallkarte

router = APIRouter()
logger = logging.getLogger(__name__)


class ResponseBody(BaseModel):
    stallkarte: ResponseBodyStallkarte | None


@router.get(
    "/find-stallkarte",
    response_model=ResponseBody,
    name="Find a Stallkarte by its ID",
    description="Retrieve a Stallkarte by its ID for the authenticated user",
    tags=["Stallkarte", "User"],
    responses={
        401: {"description": "Authentication required or invalid token"},
        403: {"description": "Permission denied to access Stallkarten"},
        422: {"description": "Request validation error"},
    },
)
def handler(
    id: int,
    user: domain.User = Depends(dependencies.authenticate),
    db: Database = Depends(dependencies.database),
) -> ResponseBody:
    holding = db.agricultural_holding_repository.get_holding_by_owner(user.id)

    if holding is None:
        logger.warning(
            f"User '{user.username}' has no agricultural holding "
            f"to retrieve a Stallkarte for"
        )
        return ResponseBody(stallkarte=None)

    stallkarte = db.stallkarte_repository.get_stallkarte_by_id(id)
    if stallkarte is None:
        logger.warning(f"Stallkarte ID '{id}' not found for user '{user.username}'")
        return ResponseBody(stallkarte=None)

    if stallkarte.holding_id != holding.id:
        logger.warning(
            f"User '{user.username}' attempted to access Stallkarte ID '{id}' "
            "which does not belong to their agricultural holding"
        )
        raise HTTPException(403, "permission denied to access this Stallkarte")

    logger.info(f"Retrieved Stallkarte ID '{id}' for user '{user.username}'")

    response_stallkarte = ResponseBodyStallkarte.from_domain(stallkarte)

    return ResponseBody(stallkarte=response_stallkarte)
