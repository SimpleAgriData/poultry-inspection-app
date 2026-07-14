from app.domain import Farm, FarmType
from app.domain.stallkarte.event import Event
from app.domain.stallkarte.events import (
    AlarmTestPerformed,
    AmbientClimateRecorded,
    DetailsRevised,
    FatteningDayDataRecorded,
    FatteningFarmAssigned,
    FeedConsumptionRecorded,
    FinishNotesReplaced,
    Finished,
    FlockTransferred,
    GeneralNotesReplaced,
    InstallationDetailsReplaced,
    LightingProgramPerformed,
    MortalityRecorded,
    PestControlMeasuresApplied,
    RearingFarmAssigned,
    Reopened,
    SectionNoteLogged,
    SiloCleaned,
    StableDisinfected,
    StallkarteStarted,
    TransferDetailsRevised,
    WaterConsumptionRecorded,
    WaterLineDisinfected,
    WeightRecorded,
    models,
)
from app.domain.stallkarte.events.dailyevents.mortality_recorded import (
    MortalityRecordedShift,
)
from app.domain.stallkarte.stallkarte import Stallkarte
from app.domain.stallkarte.stallkarte_state import (
    StallkarteAlarmTest,
    StallkarteChecklist,
    StallkarteCycle,
    StallkarteFarm,
    StallkarteLightingProgram,
    StallkartePestControlMeasures,
    StallkarteSection,
    StallkarteSiloCleaned,
    StallkarteStableDisinfected,
    StallkarteStateDay,
    StallkarteStateDaySection,
    StallkarteTransfer,
    StallkarteWaterLineDisinfected,
)


def if_not_none[T](value: T | None, /, *, else_: T | None = None) -> T | None:
    return value if value is not None else else_


class StallkarteAggregator:
    """
    Aggregates events to maintain the current state of a Stallkarte.
    """

    def __init__(self, stallkarte: Stallkarte, farms: dict[int, "Farm"]) -> None:
        self.stallkarte = stallkarte
        self.farms = farms

    @staticmethod
    def apply_to(
        stallkarte: Stallkarte,
        farms: list["Farm"],
        events: list[Event],
    ) -> None:
        farm_lookup = {f.id: f for f in farms}
        aggregator = StallkarteAggregator(stallkarte, farm_lookup)
        aggregator.apply_all(events)

    def apply_all(self, events: list[Event]) -> None:
        for event in events:
            self.apply(event)

    def resolve_farm(
        self, event: RearingFarmAssigned | FatteningFarmAssigned
    ) -> "StallkarteFarm":
        farm = StallkarteFarm(
            id=event.farm_id,
            name=event.farm_name,
            type=FarmType(event.farm_type.value),
            vvvo_number=event.farm_vvvo_number,
            sections=[
                StallkarteSection(
                    id=section.id,
                    number=section.number,
                    name=section.name,
                )
                for section in event.sections
            ],
        )
        if existing_farm := self.farms.get(event.farm_id):
            # Only overwrite the name to keep it up to date. Other fields
            # should not change, as they are authoritative from the event.
            farm.name = existing_farm.name

        return farm

    def day(self, production_day: int) -> StallkarteStateDay:
        state = self.stallkarte.state

        cycle = StallkarteCycle.REARING
        if state.transfer is not None:
            if production_day >= state.transfer.production_day:
                cycle = StallkarteCycle.FATTENING

        return state.days.setdefault(
            production_day,
            StallkarteStateDay.default(production_day, cycle),
        )

    def section(
        self, production_day: int, section_number: int
    ) -> StallkarteStateDaySection:
        day = self.day(production_day)
        return day.sections.setdefault(
            section_number,
            StallkarteStateDaySection.default(section_number),
        )

    def checklist(self, cycle: models.ChecklistCycle) -> StallkarteChecklist:
        match cycle:
            case models.ChecklistCycle.REARING:
                if self.stallkarte.state.rearing_checklist is None:
                    self.stallkarte.state.rearing_checklist = (
                        StallkarteChecklist.default()
                    )
                return self.stallkarte.state.rearing_checklist
            case models.ChecklistCycle.FATTENING:
                if self.stallkarte.state.fattening_checklist is None:
                    self.stallkarte.state.fattening_checklist = (
                        StallkarteChecklist.default()
                    )
                return self.stallkarte.state.fattening_checklist
            case _:
                raise ValueError(f"unknown checklist cycle: {cycle}")

    # This is the domain apply function, as well as the processing function for the
    # reading model. May be split up in the future if needed.
    def apply(self, event: Event) -> None:  # noqa: C901
        state = self.stallkarte.state

        payload = event.data

        match payload:
            case StallkarteStarted():
                state.date_hatched = payload.date_hatched
                state.hatchery = payload.hatchery_name
                state.breed = payload.breed
                state.fattening_cycle = payload.fattening_cycle
                state.eco_control_number = payload.eco_control_number
                state.is_eu_bio = payload.is_eu_bio
                state.is_naturland = payload.is_naturland
                state.date_started = payload.date_started
                state.is_started = True
            case DetailsRevised():
                state.date_hatched = payload.date_hatched
                state.hatchery = payload.hatchery_name
                state.breed = payload.breed
                state.fattening_cycle = payload.fattening_cycle
                state.is_eu_bio = payload.is_eu_bio
                state.is_naturland = payload.is_naturland
            case InstallationDetailsReplaced():
                state.installation_details_by_section = {
                    details.section_number: details
                    for details in payload.section_details
                }
            case FatteningFarmAssigned():
                state.fattening_farm = self.resolve_farm(payload)
            case RearingFarmAssigned():
                state.rearing_farm = self.resolve_farm(payload)
            case FlockTransferred():
                state.current_cycle = StallkarteCycle.FATTENING

                if state.date_started is not None:
                    production_date_delta = payload.transfer_date - state.date_started
                    production_day = production_date_delta.days
                    state.transfer = StallkarteTransfer(
                        date=payload.transfer_date,
                        production_day=production_day,
                        animals_by_section_number=payload.animals_by_section,
                    )

                    # Mark all days after the transfer as fattening
                    for production_day in range(
                        production_day,
                        max(state.days.keys(), default=0) + 1,
                    ):
                        day = state.days.get(production_day)
                        if day is None:
                            continue
                        day.production_cycle = StallkarteCycle.FATTENING
            case TransferDetailsRevised():
                if state.date_started is not None and state.transfer is not None:
                    state.transfer.animals_by_section_number = (
                        payload.animals_by_section
                    )
            case AmbientClimateRecorded():
                day = self.day(payload.production_day)
                day.temperature_celsius = if_not_none(
                    payload.temperature_celsius, else_=day.temperature_celsius
                )
                day.humidity_percent = if_not_none(
                    payload.humidity_percent, else_=day.humidity_percent
                )
            case FatteningDayDataRecorded():
                day = self.day(payload.production_day)
                day.opening_time = payload.opening_time
                day.weather_conditions = payload.weather_conditions
                day.veterinarian = payload.veterinarian
            case WeightRecorded():
                day = self.day(payload.production_day)
                day.weight_grams = payload.weight_grams
            case FeedConsumptionRecorded():
                day = self.day(payload.production_day)
                day.feed_consumption_kg = payload.amount_kg
            case WaterConsumptionRecorded():
                day = self.day(payload.production_day)
                day.water_consumption_liters = payload.amount_liters
            case MortalityRecorded():
                section = self.section(payload.production_day, payload.section_number)

                match payload.shift:
                    case MortalityRecordedShift.MORNING:
                        section.natural_mortality_morning = if_not_none(
                            payload.natural_deaths,
                            else_=section.natural_mortality_morning,
                        )
                        section.selective_mortality_morning = if_not_none(
                            payload.selective_deaths,
                            else_=section.selective_mortality_morning,
                        )
                        section.did_inspection_morning = (
                            section.natural_mortality_morning is not None
                            and section.selective_mortality_morning is not None
                        )
                    case MortalityRecordedShift.EVENING:
                        section.natural_mortality_evening = if_not_none(
                            payload.natural_deaths,
                            else_=section.natural_mortality_evening,
                        )
                        section.selective_mortality_evening = if_not_none(
                            payload.selective_deaths,
                            else_=section.selective_mortality_evening,
                        )
                        section.did_inspection_evening = (
                            section.natural_mortality_evening is not None
                            and section.selective_mortality_evening is not None
                        )
            case GeneralNotesReplaced():
                day = self.day(payload.production_day)
                day.notes = payload.general_notes
            case FinishNotesReplaced():
                state.finish_notes = payload.finish_notes
            case SectionNoteLogged():
                section = self.section(payload.production_day, payload.section_number)
                section.note = payload.note
            case Finished():
                state.is_finished = True
                state.date_finished = payload.date
                state.finish_notes = payload.finish_notes
            case Reopened():
                state.is_finished = False
                state.date_finished = None
            case AlarmTestPerformed():
                checklist = self.checklist(payload.cycle)
                existing = checklist.alarm_test

                checklist.alarm_test = StallkarteAlarmTest(
                    did_emergency_power_test=if_not_none(
                        payload.did_emergency_power_test,
                        else_=existing.did_emergency_power_test,
                    ),
                    did_alarm_test=if_not_none(
                        payload.did_alarm_test,
                        else_=existing.did_alarm_test,
                    ),
                )
            case LightingProgramPerformed():
                checklist = self.checklist(payload.cycle)
                existing = checklist.lighting_program

                checklist.lighting_program = StallkarteLightingProgram(
                    did_dark_period_test=if_not_none(
                        payload.did_dark_period_test,
                        else_=existing.did_dark_period_test,
                    ),
                    had_divergence_due_to_vet=if_not_none(
                        payload.had_divergence_due_to_vet,
                        else_=existing.had_divergence_due_to_vet,
                    ),
                )
            case PestControlMeasuresApplied():
                checklist = self.checklist(payload.cycle)
                existing = checklist.pest_control_measures

                checklist.pest_control_measures = StallkartePestControlMeasures(
                    did_perform_pest_control=if_not_none(
                        payload.did_perform_pest_control,
                        else_=existing.did_perform_pest_control,
                    ),
                    annotation=if_not_none(
                        payload.annotation,
                        else_=existing.annotation,
                    ),
                )
            case SiloCleaned():
                checklist = self.checklist(payload.cycle)
                existing = checklist.silo_cleaned

                checklist.silo_cleaned = StallkarteSiloCleaned(
                    date=if_not_none(
                        payload.date,
                        else_=existing.date,
                    ),
                    detergent=if_not_none(
                        payload.detergent,
                        else_=existing.detergent,
                    ),
                    dosis=if_not_none(
                        payload.dosis,
                        else_=existing.dosis,
                    ),
                )
            case StableDisinfected():
                checklist = self.checklist(payload.cycle)
                existing = checklist.stable_disinfected

                checklist.stable_disinfected = StallkarteStableDisinfected(
                    date=if_not_none(
                        payload.date,
                        else_=existing.date,
                    ),
                    disinfectant=if_not_none(
                        payload.disinfectant,
                        else_=existing.disinfectant,
                    ),
                    dosis=if_not_none(
                        payload.dosis,
                        else_=existing.dosis,
                    ),
                )
            case WaterLineDisinfected():
                checklist = self.checklist(payload.cycle)
                existing = checklist.water_line_disinfected

                checklist.water_line_disinfected = StallkarteWaterLineDisinfected(
                    date=if_not_none(
                        payload.date,
                        else_=existing.date,
                    ),
                    disinfectant=if_not_none(
                        payload.disinfectant,
                        else_=existing.disinfectant,
                    ),
                    dosis=if_not_none(
                        payload.dosis,
                        else_=existing.dosis,
                    ),
                )
            case _:
                raise ValueError(f"unable to handle event type: {event.type}")
