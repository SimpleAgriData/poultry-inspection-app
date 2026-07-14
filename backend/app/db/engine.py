from contextlib import contextmanager
from functools import lru_cache
from typing import Generator

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import (
    ORMExecuteState,
    Session,
    with_loader_criteria,
)

from app.db.models.mixins import SoftDeletableMixin


@lru_cache
def get_engine(url: str) -> Engine:
    return create_engine(url, future=True)


@contextmanager
def create_session(engine: Engine) -> Generator[Session, None, None]:
    with Session(engine, future=True) as session:
        yield session


@event.listens_for(Session, "do_orm_execute")
def _add_filter(execute_state: ORMExecuteState) -> None:
    include_deleted = execute_state.execution_options.get("include_deleted", False)
    if include_deleted:
        return

    execute_state.statement = execute_state.statement.options(
        with_loader_criteria(
            SoftDeletableMixin,
            lambda cls: cls.deleted_at.is_(None),
            include_aliases=True,
        )
    )
