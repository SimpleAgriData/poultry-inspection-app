from pydantic import BaseModel
from sqlalchemy import select

from app import domain
from app.db import models
from app.services.database import translate
from app.services.database.repositories.repository import Repository


class SectionCandidate(BaseModel):
    name: str


class SectionRepository(Repository):
    def add_section(self, farm_id: int, candidate: SectionCandidate) -> domain.Section:
        db_section = models.Section(
            name=candidate.name,
            farm_id=farm_id,
        )
        self._add(db_section)

        return translate.section_to_domain(db_section)

    def update_section(
        self,
        section_id: int,
        candidate: SectionCandidate,
    ) -> domain.Section:
        statement = select(models.Section).where(models.Section.id == section_id)
        db_section = self.session.execute(statement).scalar_one_or_none()

        if db_section is None:
            raise ValueError(f"section with ID '{section_id}' not found")

        db_section.name = candidate.name

        self._add(db_section)

        return translate.section_to_domain(db_section)

    def delete_section(self, section_id: int) -> None:
        statement = select(models.Section).where(models.Section.id == section_id)
        db_section = self.session.execute(statement).scalar_one_or_none()
        if db_section is None:
            raise ValueError(f"section with ID '{section_id}' not found")
        self._delete(db_section)

    def get_section_by_id(
        self, section_id: int, include_deleted: bool = False
    ) -> domain.Section | None:
        statement = select(models.Section).where(models.Section.id == section_id)
        if include_deleted:
            statement = statement.execution_options(include_deleted=True)
        db_section = self.session.execute(statement).scalar_one_or_none()
        if db_section is None:
            return None
        return translate.section_to_domain(db_section)
