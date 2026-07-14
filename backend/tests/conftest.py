from typing import Any, Generator

import pytest
from fastapi import FastAPI
from sqlalchemy import Engine, StaticPool, create_engine
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app import domain
from app.api.v1 import router
from app.core import dependencies
from app.core.stallkarteexport import Exporter
from app.db.models.mixins import Base
from app.services.database import (
    AgriculturalHoldingCandidate,
    Database,
    FarmCandidate,
    FarmTypeCandidate,
    SectionCandidate,
)
from app.services.database.repositories import (
    AgriculturalHoldingRepository,
    FarmRepository,
    SectionRepository,
    StallkarteRepository,
)


@pytest.fixture
def engine() -> Engine:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine: Engine) -> Generator[Session, None, None]:
    """A fixture that provides a SQLModel session for testing"""
    with Session(engine) as session:
        yield session


@pytest.fixture
def database(session: Session) -> Database:
    """A fixture that provides a Database instance for testing"""
    return Database(session)


@pytest.fixture
def stallkarte_repository(
    database: Database,
) -> StallkarteRepository:
    """A fixture that provides the StallkarteRepository for testing"""
    return database.stallkarte_repository


@pytest.fixture
def agricultural_holding_repository(
    database: Database,
) -> AgriculturalHoldingRepository:
    """A fixture that provides the AgriculturalHoldingRepository for testing"""
    return database.agricultural_holding_repository


@pytest.fixture
def farm_repository(database: Database) -> FarmRepository:
    """A fixture that provides the FarmRepository for testing"""
    return database.farm_repository


@pytest.fixture
def section_repository(database: Database) -> SectionRepository:
    """A fixture that provides the SectionRepository for testing"""
    return database.section_repository


@pytest.fixture
def farms_5(
    farm_repository: FarmRepository,
    section_repository: SectionRepository,
    holding: domain.AgriculturalHolding,
) -> list[domain.Farm]:
    farms: list[domain.Farm] = []

    farm_candidates: list[FarmCandidate] = [
        FarmCandidate(
            type=FarmTypeCandidate.FATTENING,
            name="Farm 1",
            vvvo_number="VV100000",
        ),
        FarmCandidate(
            type=FarmTypeCandidate.FATTENING,
            name="Farm 2",
            vvvo_number="VV100001",
        ),
        FarmCandidate(
            type=FarmTypeCandidate.REARING,
            name="Farm 3",
            vvvo_number="VV100002",
        ),
        FarmCandidate(
            type=FarmTypeCandidate.REARING,
            name="Farm 4",
            vvvo_number="VV100003",
        ),
        FarmCandidate(
            type=FarmTypeCandidate.COMBINED,
            name="Farm 5",
            vvvo_number="VV100004",
        ),
    ]

    sections_candidates: list[SectionCandidate] = [
        SectionCandidate(
            name="Section 1",
        ),
        SectionCandidate(
            name="Section 2",
        ),
    ]

    for farm_candidate in farm_candidates:
        farm = farm_repository.add_farm(holding.id, farm_candidate)

        for section_candidate in sections_candidates:
            section_repository.add_section(farm.id, section_candidate)

        db_farm = farm_repository.get_farm_by_id(farm.id)
        if db_farm is None:
            raise ValueError(f"farm with id {farm.id} not found after creation")

        farms.append(db_farm)

    return farms


@pytest.fixture
def holding_farms_5(
    farms_5: list[domain.Farm],
) -> domain.AgriculturalHolding:
    # A little cheesy, but it works
    return farms_5[0].holding


@pytest.fixture
def user() -> domain.User:
    return domain.User(
        id="testuser", username="testuser", firstname="Test", lastname="User"
    )


@pytest.fixture
def holding(
    agricultural_holding_repository: AgriculturalHoldingRepository,
    user: domain.User,
) -> domain.AgriculturalHolding:
    holding_candidate = AgriculturalHoldingCandidate(
        owner_user_id=user.id,
        name="Sunny Farm",
        hatchery="Happy Hatchery",
        eco_control_number="EC123456",
        breed="Lohmann Brown",
        address_street="123 Farm Lane",
        address_zip="12345",
        address_city="Farmville",
    )
    holding = agricultural_holding_repository.add_holding(holding_candidate)
    return holding


@pytest.fixture
def other_holding(
    agricultural_holding_repository: AgriculturalHoldingRepository,
) -> domain.AgriculturalHolding:
    holding_candidate = AgriculturalHoldingCandidate(
        owner_user_id="other_farmer",
        name="Other Farm",
        hatchery="Other Hatchery",
        eco_control_number="EC654321",
        breed="Rheinlander",
        address_street="456 Other Lane",
        address_zip="54321",
        address_city="Otherville",
    )
    holding = agricultural_holding_repository.add_holding(holding_candidate)
    return holding


@pytest.fixture
def exporter() -> Exporter:
    return Exporter("res/stallkarte_template.xlsx", "Stallkarte TEMPLATE")


@pytest.fixture
def app(user: domain.User, database: Database, exporter: Exporter) -> FastAPI:
    app = FastAPI()
    app.include_router(router)

    app.dependency_overrides[dependencies.authenticate] = lambda: user
    app.dependency_overrides[dependencies.database] = lambda: database
    app.dependency_overrides[dependencies.exporter] = lambda: exporter

    return app


@pytest.fixture
def client(app: FastAPI) -> Generator[TestClient, Any, None]:
    with TestClient(app) as test_client:
        yield test_client
