from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

from app.core.config import get_settings
from app.core.stallkarte_export_import.importer import Importer
from app.db import create_session, get_engine
from app.db.models.mixins import Base
from app.services.database import Database


parser = argparse.ArgumentParser(
    description="Import a Stallkarte workbook directly into the database"
)
parser.add_argument("file_path", help="Path to the exported workbook")
parser.add_argument(
    "--holding-id",
    type=int,
    required=True,
    help="ID of the agricultural holding to import into",
)
parser.add_argument(
    "--database-url",
    default=None,
    help="Optional database URL override instead of the configured default",
)


def main() -> int:
    args = parser.parse_args()

    settings = get_settings()
    database_url = args.database_url or settings.db.url

    engine = get_engine(database_url)
    Base.metadata.create_all(engine)

    importer = Importer(Path(args.file_path))

    with create_session(engine) as session:
        db = Database(session)
        holding = db.agricultural_holding_repository.get_holding_by_id(args.holding_id)

        if holding is None:
            raise ValueError(f"holding with id {args.holding_id} not found")

        result = importer.import_stallkarte(
            holding,
            db,
        )

        session.commit()

    sys.stdout.write(
        "Imported stallkarte {stallkarte_id} with events\n".format(
            stallkarte_id=result.id,
            
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())