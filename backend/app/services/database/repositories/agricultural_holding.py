from pydantic import BaseModel, ConfigDict
from sqlalchemy import select

from app import domain
from app.db import models
from app.services.database.repositories.repository import Repository
from app.services.database.translate import translate


class AgriculturalHoldingCandidate(BaseModel):
    model_config = ConfigDict(frozen=True)

    owner_user_id: str
    name: str
    hatchery: str
    eco_control_number: str
    breed: str
    address_street: str
    address_zip: str
    address_city: str


class AgriculturalHoldingRepository(Repository):
    def add_holding(
        self, candidate: AgriculturalHoldingCandidate
    ) -> domain.AgriculturalHolding:
        db_holding = models.AgriculturalHolding(
            owner_user_id=candidate.owner_user_id,
            name=candidate.name,
            hatchery=candidate.hatchery,
            eco_control_number=candidate.eco_control_number,
            breed=candidate.breed,
            address_street=candidate.address_street,
            address_zip=candidate.address_zip,
            address_city=candidate.address_city,
        )

        self._add(db_holding)

        return translate.holding_to_domain(db_holding)

    def update_holding(
        self,
        holding_id: int,
        candidate: AgriculturalHoldingCandidate,
    ) -> domain.AgriculturalHolding:
        statement = select(models.AgriculturalHolding).where(
            models.AgriculturalHolding.id == holding_id
        )
        db_holding = self.session.execute(statement).scalar_one_or_none()

        if db_holding is None:
            raise ValueError(f"agricultural holding with ID '{holding_id}' not found")

        db_holding.owner_user_id = candidate.owner_user_id
        db_holding.name = candidate.name
        db_holding.hatchery = candidate.hatchery
        db_holding.eco_control_number = candidate.eco_control_number
        db_holding.breed = candidate.breed
        db_holding.address_street = candidate.address_street
        db_holding.address_zip = candidate.address_zip
        db_holding.address_city = candidate.address_city

        self._add(db_holding)
        return translate.holding_to_domain(db_holding)

    def all_holdings(self) -> list[domain.AgriculturalHolding]:
        statement = select(models.AgriculturalHolding)
        db_holdings = self.session.execute(statement).scalars().all()
        return [translate.holding_to_domain(db_holding) for db_holding in db_holdings]

    def get_holding_by_id(self, holding_id: int) -> domain.AgriculturalHolding | None:
        statement = select(models.AgriculturalHolding).where(
            models.AgriculturalHolding.id == holding_id
        )
        db_holding = self.session.execute(statement).scalar_one_or_none()

        if db_holding is None:
            return None

        return translate.holding_to_domain(db_holding)

    def get_holding_by_owner(
        self, owner_user_id: str
    ) -> domain.AgriculturalHolding | None:
        statement = select(models.AgriculturalHolding).where(
            models.AgriculturalHolding.owner_user_id == owner_user_id
        )
        db_holding = self.session.execute(statement).scalar_one_or_none()

        if db_holding is None:
            return None

        return translate.holding_to_domain(db_holding)
