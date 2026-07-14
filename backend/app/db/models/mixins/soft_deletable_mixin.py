import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column


class SoftDeletableMixin:
    """A mixin that adds soft delete functionality to a model"""

    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), index=True, nullable=True
    )

    @property
    def is_deleted(self) -> bool:
        """Helper property to check status"""
        return self.deleted_at is not None
