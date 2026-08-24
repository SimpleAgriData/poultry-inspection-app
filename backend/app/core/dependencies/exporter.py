from fastapi import Depends

from app.core.config import StallkarteConfig
from app.core.dependencies import settings
from app.core.stallkarte_export_import import Exporter


def exporter(
    stallkarte: StallkarteConfig = Depends(settings.stallkarte_config),
) -> Exporter:
    return Exporter(
        template_file=stallkarte.template_file,
        template_file_default_worksheet=stallkarte.template_file_default_worksheet,
    )
