import logging
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app import domain
from app.core import dependencies
from app.core.stallkarte_export_import import Exporter
from app.services.database import Database

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/export-stallkarte",
    name="Export a Stallkarte as Excel file",
    description="Export a Stallkarte as an Excel file for the authenticated user",
    tags=["Stallkarte"],
    responses={
        401: {"description": "Authentication required or invalid token"},
        403: {"description": "Permission denied to access Stallkarte"},
        422: {"description": "Request validation error"},
    },
)
def handler(
    stallkarte_id: int,
    user: domain.User = Depends(dependencies.authenticate),
    db: Database = Depends(dependencies.database),
    exporter: Exporter = Depends(dependencies.exporter),
) -> StreamingResponse:
    stallkarte = db.stallkarte_repository.get_stallkarte_by_id(stallkarte_id)
    if stallkarte is None:
        raise HTTPException(404, f"stallkarte ID '{stallkarte_id}' not found")

    holding = db.agricultural_holding_repository.get_holding_by_owner(user.id)
    if holding is None:
        raise HTTPException(
            404,
            "user has no associated agricultural holding",
        )

    if stallkarte.holding_id != holding.id:
        raise HTTPException(
            403,
            f"stallkarte ID '{stallkarte_id}' does not belong to the user's holding",
        )

    wb = exporter.export(holding, stallkarte)

    file_bytes = BytesIO()

    try:
        wb.save(file_bytes)
    except ValueError as e:
        logger.warning("Cannot export Stallkarte ID '%s': %s", stallkarte_id, e)
        raise HTTPException(
            status_code=422,
            detail=e.args[0] if e.args else "Invalid data in Stallkarte for export",
        )
    except Exception as e:
        logger.error(
            f"Error while generating export file for "
            f"Stallkarte ID '{stallkarte_id}': {e}"
        )
        raise HTTPException(500, "failed to generate export file")

    logger.info(f"Stallkarte ID '{stallkarte_id}' exported successfully")

    headers = {
        "Content-Disposition": f"attachment; "
        f"filename=stallkarte_{stallkarte.state.fattening_cycle}.xlsx"
    }

    return StreamingResponse(
        iter([file_bytes.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )
