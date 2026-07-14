import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app import domain
from app.api.v1.commands.stallkarte.setup import setup_stallkarte
from app.core import dependencies
from app.services.database import Database
from app.shared.api import MessageResponse

router = APIRouter()
logger = logging.getLogger(__name__)


class RequestBody(BaseModel):
    stallkarte_id: int = Field(gt=0, description="ID of the Stallkarte to delete")


@router.post(
    "/delete-stallkarte",
    response_model=MessageResponse,
    name="Delete Stallkarte",
    description="Delete an existing finished Stallkarte",
    responses={
        400: {"description": "Bad request"},
        401: {"description": "Authentication required or invalid token"},
        403: {"description": "Permission denied"},
        404: {"description": "Stallkarte not found"},
        422: {"description": "Request body validation error"},
    },
)
def handler(
    request_body: RequestBody,
    user: domain.User = Depends(dependencies.authenticate),
    db: Database = Depends(dependencies.database),
) -> MessageResponse:
    stallkarte, _holding = setup_stallkarte(db, user.id, request_body.stallkarte_id)

    if not stallkarte.state.is_finished:
        raise HTTPException(400, "only finished stallkarten can be deleted")

    db.stallkarte_repository.delete_stallkarte(stallkarte.id)

    logger.info(f"Stallkarte ID '{stallkarte.id}' deleted by user '{user.username}'")

    return MessageResponse(message="Stallkarte deleted successfully")
