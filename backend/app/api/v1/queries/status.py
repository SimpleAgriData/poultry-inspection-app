from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.config import Settings, get_settings

router = APIRouter()


class ResponseModel(BaseModel):
    status: Literal["ok"]
    version: str
    git_version: str


@router.get(
    "/status",
    response_model=ResponseModel,
    name="Status",
    description="Service status endpoint",
    tags=["Status"],
)
def get_status(settings: Settings = Depends(get_settings)) -> ResponseModel:
    return ResponseModel(
        status="ok", version=settings.app.version, git_version=settings.app.git_version
    )
