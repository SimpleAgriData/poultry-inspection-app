import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app import domain
from app.core import dependencies
from app.services import database
from app.services.database import Database
from app.core.stallkarte_export_import import Importer
from app.core.stallkarte_export_import.errors import StallkarteImportError

router = APIRouter()
logger = logging.getLogger(__name__)



class ResponseBody(BaseModel):
    message: str


@router.post(
    "/import-stallkarte",
    response_model=ResponseBody,
    name="Import Stallkarte",
    description="Import a Durchgangsbericht excel file",
    tags=["Stallkarte"],
    responses={
        401: {"description": "Authentication required or invalid token"},
        403: {"description": "Permission denied to import stallkarte"},
        404: {"description": "Not found"},
        422: {"description": "Request body validation error"},
    },
) 
async def handler(
    file: UploadFile,
    user: domain.User = Depends(dependencies.authenticate),
    db: Database = Depends(dependencies.database),
) -> ResponseBody:
    await file.seek(0)

    importer = Importer(file.file)
    holding = db.agricultural_holding_repository.get_holding_by_owner(user.id)
    if holding is None:
        raise HTTPException(404, f"agricultural holding for user '{user.username}' not found")
    try:
        imported_stallkarte = importer.import_stallkarte(holding, db)
        db.session.commit()
        logger.info(
                f"File '{file.filename}' imported successfully for user '{user.username}' and holding '{holding.name}' as Stallkarte ID '{imported_stallkarte.id}'"
            )
        return ResponseBody(message=f"Stallkarte '{imported_stallkarte.id}' imported successfully")

    
    except StallkarteImportError as error:
        db.session.rollback()
        logger.info(
                        f"Import failed for File '{file.filename}'. Error: {error.code} - {error.message}"
                    )
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": error.code,
                    "message": error.message,
                    "german_display_message": error.german_display_message,
                }
            },
        )
    finally:
            await file.close()
   