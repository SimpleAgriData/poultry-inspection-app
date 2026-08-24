from enum import StrEnum, auto

from pydantic import BaseModel
from sqlalchemy import select

from app import domain
from app.db import models
from app.services.database import translate
from app.services.database.repositories.repository import Repository


class FarmTypeCandidate(StrEnum):
    FATTENING = auto()
    REARING = auto()
    COMBINED = auto()


class FarmCandidate(BaseModel):
    type: FarmTypeCandidate
    name: str
    vvvo_number: str


def _to_farm_type(farm_type_candidate: FarmTypeCandidate) -> models.FarmType:
    match farm_type_candidate:
        case FarmTypeCandidate.FATTENING:
            return models.FarmType.FATTENING
        case FarmTypeCandidate.REARING:
            return models.FarmType.REARING
        case FarmTypeCandidate.COMBINED:
            return models.FarmType.COMBINED
        case _:
            raise ValueError(f"unknown FarmTypeCandidate: {farm_type_candidate}")


class FarmRepository(Repository):
    def add_farm(self, holding_id: int, candidate: FarmCandidate) -> domain.Farm:
        db_farm = models.Farm(
            name=candidate.name,
            type=_to_farm_type(candidate.type),
            holding_id=holding_id,
            vvvo_number=candidate.vvvo_number,
        )
        self._add(db_farm)

        return translate.farm_to_domain(db_farm)

    def update_farm(
        self,
        farm_id: int,
        candidate: FarmCandidate,
    ) -> domain.Farm:
        statement = select(models.Farm).where(models.Farm.id == farm_id)
        db_farm = self.session.execute(statement).scalar_one_or_none()

        if db_farm is None:
            raise ValueError(f"farm with ID '{farm_id}' not found")

        db_farm.name = candidate.name
        db_farm.type = _to_farm_type(candidate.type)
        db_farm.vvvo_number = candidate.vvvo_number

        self._add(db_farm)

        return translate.farm_to_domain(db_farm)

    def delete_farm(self, farm_id: int) -> None:
        statement = select(models.Farm).where(models.Farm.id == farm_id)
        db_farm = self.session.execute(statement).scalar_one_or_none()
        if db_farm is None:
            raise ValueError(f"farm with ID '{farm_id}' not found")
        self._delete(db_farm)

    def get_farm_by_id(
        self, farm_id: int, include_deleted: bool = False
    ) -> domain.Farm | None:
        statement = select(models.Farm).where(models.Farm.id == farm_id)
        if include_deleted:
            statement = statement.execution_options(include_deleted=True)
        db_farm = self.session.execute(statement).scalar_one_or_none()
        if db_farm is None:
            return None
        return translate.farm_to_domain(db_farm)

    def get_farm_id_by_vvonr(
        self, vvvo_number: str | int, include_deleted: bool = False
    ) -> int | None:
        if vvvo_number is None:
            raise ValueError("vvvo_number must be provided")

        normalized_vvvo_number = str(vvvo_number).strip()
        statement = select(models.Farm.id).where(
            models.Farm.vvvo_number == normalized_vvvo_number
        )
        if include_deleted:
            statement = statement.execution_options(include_deleted=True)
        db_farm_id = self.session.execute(statement).scalar_one_or_none()
        return db_farm_id

    def get_farms_by_holding_id(
        self, holding_id: int, include_deleted: bool = False
    ) -> list[domain.Farm]:
        statement = select(models.Farm).where(models.Farm.holding_id == holding_id)
        if include_deleted:
            statement = statement.execution_options(include_deleted=True)
        db_farms = self.session.execute(statement).scalars().all()
        return [translate.farm_to_domain(db_farm) for db_farm in db_farms]
    
