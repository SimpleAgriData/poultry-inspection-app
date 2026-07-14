import datetime

import pytest

from app.domain import (
    AgriculturalHolding,
    Farm,
    FarmType,
    Stallkarte,
    StallkarteAggregator,
    StallkarteState,
)


@pytest.fixture
def stallkarte(holding: AgriculturalHolding) -> Stallkarte:
    state = StallkarteState.default()
    return Stallkarte(id=0, holding_id=holding.id, state=state)


@pytest.fixture
def aggregator(farms_5: list[Farm]) -> StallkarteAggregator:
    holding = farms_5[0].holding
    state = StallkarteState.default()
    stallkarte = Stallkarte(id=0, holding_id=holding.id, state=state)
    farms = {f.id: f for f in farms_5}
    return StallkarteAggregator(stallkarte, farms)


@pytest.fixture
def started_aggregator(aggregator: StallkarteAggregator) -> StallkarteAggregator:
    today = datetime.date.today()

    events = aggregator.stallkarte.start_stallkarte(
        date_started=today,
        date_hatched=today,
        hatchery_name="Happy Hatchery",
        breed="Broiler",
        fattening_cycle="Fattening Cycle 1",
        eco_control_number="ECO123456",
        is_eu_bio=True,
        is_naturland=False,
    )
    aggregator.apply_all(events)

    return aggregator


@pytest.fixture
def rearing_farm(aggregator: StallkarteAggregator) -> Farm | None:
    for farm in aggregator.farms.values():
        if farm.type == FarmType.REARING:
            return farm

    raise ValueError("no rearing farm found in aggregator")


@pytest.fixture
def fattening_farm(aggregator: StallkarteAggregator) -> Farm | None:
    for farm in aggregator.farms.values():
        if farm.type == FarmType.FATTENING:
            return farm

    raise ValueError("no fattening farm found in aggregator")


@pytest.fixture
def combined_farm(aggregator: StallkarteAggregator) -> Farm | None:
    for farm in aggregator.farms.values():
        if farm.type == FarmType.COMBINED:
            return farm

    raise ValueError("no combined farm found in aggregator")
