from app import domain
from app.db import models
from app.domain.stallkarte import parse_event


def holding_to_domain(
    db_holding: models.AgriculturalHolding,
) -> domain.AgriculturalHolding:
    domain_holding = domain.AgriculturalHolding(
        id=db_holding.id or 0,
        owner_user_id=db_holding.owner_user_id,
        name=db_holding.name,
        hatchery=db_holding.hatchery,
        eco_control_number=db_holding.eco_control_number,
        breed=db_holding.breed,
        address_street=db_holding.address_street,
        address_zip=db_holding.address_zip,
        address_city=db_holding.address_city,
        farms=[],
    )

    farms: list[domain.Farm] = []
    for farm in db_holding.farms:
        farms.append(farm_to_domain(farm, parent_holding=domain_holding))

    domain_holding.farms = farms
    return domain_holding


def farm_to_domain(
    db_farm: models.Farm, parent_holding: domain.AgriculturalHolding | None = None
) -> domain.Farm:
    domain_farm = domain.Farm(
        id=db_farm.id or 0,
        name=db_farm.name,
        type=farm_type_to_domain(db_farm.type),
        holding=parent_holding or holding_to_domain(db_farm.holding),
        vvvo_number=db_farm.vvvo_number,
        sections=[],
    )

    sections: list[domain.Section] = []
    for section in db_farm.sections:
        sections.append(section_to_domain(section, parent_farm=domain_farm))

    domain_farm.sections = sections
    return domain_farm


def farm_type_to_domain(db_farm_type: models.FarmType) -> domain.FarmType:
    mapping = {
        models.FarmType.FATTENING: domain.FarmType.FATTENING,
        models.FarmType.REARING: domain.FarmType.REARING,
        models.FarmType.COMBINED: domain.FarmType.COMBINED,
    }
    return mapping[db_farm_type]


def section_to_domain(
    db_section: models.Section, parent_farm: domain.Farm | None = None
) -> domain.Section:
    return domain.Section(
        id=db_section.id or 0,
        name=db_section.name,
        farm=parent_farm or farm_to_domain(db_section.farm),
    )


def stallkarte_to_domain(
    db_stallkarte: models.Stallkarte,
) -> domain.Stallkarte:
    stallkarte = domain.Stallkarte(
        id=db_stallkarte.id or 0,
        holding_id=db_stallkarte.holding_id,
        state=domain.StallkarteState.default(),
    )

    holding = holding_to_domain(db_stallkarte.holding)

    farms: dict[int, domain.Farm] = {}
    for farm in db_stallkarte.holding.farms:
        farms[farm.id] = farm_to_domain(farm, parent_holding=holding)

    aggregator = domain.StallkarteAggregator(
        stallkarte=stallkarte,
        farms=farms,
    )

    for db_event in db_stallkarte.events:
        event = parse_event(db_event.type, db_event.data)
        aggregator.apply(event)

    return stallkarte


def shallow_stallkarte_to_domain(
    db_stallkarte: models.Stallkarte,
) -> domain.ShallowStallkarte:
    """
    This function assumes that only the relevant events for a shallow stallkarte are
    included.
    :param db_stallkarte:
    :return:
    """
    stallkarte = stallkarte_to_domain(db_stallkarte)

    return domain.ShallowStallkarte(
        id=stallkarte.id,
        holding_id=stallkarte.holding_id,
        date_started=stallkarte.state.date_started,
        date_hatched=stallkarte.state.date_hatched,
        hatchery_name=stallkarte.state.hatchery,
        breed=stallkarte.state.breed,
        fattening_cycle=stallkarte.state.fattening_cycle,
        eco_control_number=stallkarte.state.eco_control_number,
        is_eu_bio=stallkarte.state.is_eu_bio,
        is_naturland=stallkarte.state.is_naturland,
        is_finished=db_stallkarte.is_finished,
        date_finished=stallkarte.state.date_finished,
    )
