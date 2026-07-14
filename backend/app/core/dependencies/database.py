from typing import Generator

from fastapi import Depends

from app.core.config import DatabaseConfig
from app.core.dependencies import settings
from app.db import create_session, get_engine
from app.services.database import Database


# The @contextmanager decorator is explicitly not used here since it seems
# to break FastAPI's dependency injection system.
def database(
    db_config: DatabaseConfig = Depends(settings.database_config),
) -> Generator[Database, None, None]:
    engine = get_engine(db_config.url)
    with create_session(engine) as session:
        yield Database(session)
