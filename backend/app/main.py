import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import domain
from app.core import setup_logging
from app.core.config import (
    get_settings,
)
from app.db import get_engine
from app.db.models.mixins import Base
from app.router import router

setup_logging()
logger = logging.getLogger(__name__)


settings = get_settings()
engine = get_engine(settings.db.url)


Base.metadata.create_all(engine)

app = FastAPI(
    title=settings.app.name,
    version=settings.app.version,
    description=settings.app.description,
    openapi_url="/.well-known/openapi",
)
app.add_middleware(
    # TODO: This is a known ty-error: https://github.com/astral-sh/ty/issues/1635
    # Remove when fixed
    CORSMiddleware,  # ty:ignore[invalid-argument-type]
    allow_origins=settings.server.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(domain.Exception)
async def domain_exception_handler(
    request: Request, exc: domain.Exception
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message, "type": "Domain Exception"},
    )


app.include_router(router)
