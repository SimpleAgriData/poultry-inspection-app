import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel

from app.domain.exception import DomainException
from app.domain.farm import FarmType
from app.domain.stallkarte.event import Event
from app.domain.stallkarte.events import (
    AlarmTestPerformed,
    AmbientClimateRecorded,
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
    WaterConsumptionRecorded,
    WaterLineDisinfected,
    WeightRecorded,
    models,
)
from app.domain.stallkarte.events.dailyevents.mortality_recorded import (
    MortalityRecordedShift,
)
from app.domain.stallkarte.events.details_revised import DetailsRevised
from app.domain.stallkarte.events.transfer_details_revised import TransferDetailsRevised
from app.domain.stallkarte.stallkarte_state import (
    StallkarteCycle,
    StallkarteState,
)

if TYPE_CHECKING:
    from app.domain import Farm


# noinspection PyMethodMayBeStatic
class Stallkarte(BaseModel):
    """
    This is the central Stallkarte aggregate. It contains all business logic for
    managing a Stallkarte's lifecycle, including assigning farms, starting the
    stallkarte, transferring flocks, recording daily events, and finishing the
    stallkarte.

    Domain rules and validations are enforced within the methods of this class to ensure
    that the Stallkarte remains in a consistent and valid state throughout its
    lifecycle.
    """

    id: int
    holding_id: int
    state: StallkarteState

    @staticmethod
    def _validate_installation_details(
        section_details: list[models.SectionInstallationDetails],
    ) -> None:
        for details in section_details:
            if details.initial_animals_count <= 0:
                raise DomainException(
                    "initial_animals_count must be greater than 0 for each section"
                )
            if details.initial_weight_grams <= 0:
                raise DomainException(
                    "initial_weight_grams must be greater than 0 for each section"
                )
            if details.bedding.strip() == "":
                raise DomainException("bedding must be provided for each section")
            for parent_flock in details.parent_flocks:
                if parent_flock.production_week <= 0:
                    raise DomainException(
                        "production_week must be greater than 0 for each parent flock"
                    )
                if parent_flock.herd_identifier.strip() == "":
                    raise DomainException(
                        "herd_identifier must be provided for each parent flock"
                    )

    def start_stallkarte(
        self,
        date_started: datetime.date,
        date_hatched: datetime.date,
        hatchery_name: str,
        breed: str,
        fattening_cycle: str,
        eco_control_number: str,
        is_eu_bio: bool,
        is_naturland: bool,
    ) -> list["Event"]:
        if self.state.is_started:
            raise DomainException("stallkarte has already been started")

        return [
            StallkarteStarted(
                date_started=date_started,
                date_hatched=date_hatched,
                hatchery_name=hatchery_name,
                breed=breed,
                fattening_cycle=fattening_cycle,
                eco_control_number=eco_control_number,
                is_eu_bio=is_eu_bio,
                is_naturland=is_naturland,
            ).event(),
        ]

    def revise_details(
        self,
        date_hatched: datetime.date,
        hatchery_name: str,
        breed: str,
        fattening_cycle: str,
        is_eu_bio: bool,
        is_naturland: bool,
    ) -> list["Event"]:
        if not self.state.is_started:
            raise DomainException("stallkarte has not been started yet")

        return [
            DetailsRevised(
                date_hatched=date_hatched,
                hatchery_name=hatchery_name,
                breed=breed,
                fattening_cycle=fattening_cycle,
                is_eu_bio=is_eu_bio,
                is_naturland=is_naturland,
            ).event(),
        ]

    def replace_installation_details(
        self,
        section_details: list[models.SectionInstallationDetails],
    ) -> list["Event"]:
        if not self.state.is_started:
            raise DomainException("stallkarte has not been started yet")

        if self.state.rearing_farm is None:
            raise DomainException("rearing farm is not assigned")

        expected_section_numbers = {
            section.number for section in self.state.rearing_farm.sections
        }
        provided_section_numbers = {
            details.section_number for details in section_details
        }

        if expected_section_numbers != provided_section_numbers:
            raise DomainException(
                "installation details must be provided for all sections"
            )

        self._validate_installation_details(section_details)

        return [
            InstallationDetailsReplaced(
                section_details=section_details,
            ).event()
        ]

    def assign_rearing_farm(self, farm: "Farm") -> list["Event"]:
        if len(self.state.days) > 0:
            raise DomainException(
                "cannot change rearing farm after the first "
                "production day has been recorded"
            )

        if self.state.fattening_farm is not None:
            if len(self.state.fattening_farm.sections) != len(farm.sections):
                raise DomainException(
                    "rearing farm must have the same number of sections as "
                    "the fattening farm"
                )
        if farm.type not in (FarmType.REARING, FarmType.COMBINED):
            raise DomainException("assigned farm is not a rearing or combined farm")

        sections = [
            models.AssignedFarmSection(
                id=section.id,
                number=index + 1,  # This is the id-independent number of the section
                name=section.name,
            )
            for index, section in enumerate(farm.sections)
        ]

        return [
            RearingFarmAssigned(
                farm_id=farm.id,
                farm_name=farm.name,
                farm_type=models.AssignedFarmType(farm.type.value),
                farm_vvvo_number=farm.vvvo_number,
                sections=sections,
            ).event()
        ]

    def assign_fattening_farm(self, farm: "Farm") -> list["Event"]:
        if self.state.current_cycle != StallkarteCycle.REARING:
            raise DomainException(
                "cannot change fattening farm after fattening started"
            )

        if self.state.rearing_farm is not None:
            if len(self.state.rearing_farm.sections) != len(farm.sections):
                raise DomainException(
                    "fattening farm must have the same number of sections as "
                    "the rearing farm"
                )
        if farm.type not in (FarmType.FATTENING, FarmType.COMBINED):
            raise DomainException("assigned farm is not a fattening or combined farm")

        sections = [
            models.AssignedFarmSection(
                id=section.id,
                number=index + 1,  # This is the id independent number of the section
                name=section.name,
            )
            for index, section in enumerate(farm.sections)
        ]

        return [
            FatteningFarmAssigned(
                farm_id=farm.id,
                farm_name=farm.name,
                farm_type=models.AssignedFarmType(farm.type.value),
                farm_vvvo_number=farm.vvvo_number,
                sections=sections,
            ).event()
        ]

    def transfer_flock(
        self,
        transfer_date: datetime.date,
        animals_by_section_number: dict[int, int],
    ) -> list["Event"]:
        if self.state.transfer is not None:
            raise DomainException("flock has already been transferred")

        if self.state.current_cycle != StallkarteCycle.REARING:
            raise DomainException("flock has already been transferred to fattening")

        if self.state.fattening_farm is None:
            raise DomainException("fattening farm is not assigned")

        for section in self.state.fattening_farm.sections:
            if section.number not in animals_by_section_number:
                raise DomainException(
                    f"number of animals for section {section.number} not provided"
                )
            if animals_by_section_number[section.number] < 0:
                raise DomainException(
                    f"number of animals for section {section.number} must be "
                    f"non-negative"
                )

        return [
            FlockTransferred(
                transfer_date=transfer_date,
                animals_by_section=animals_by_section_number,
            ).event(),
        ]

    def revise_transfer_details(
        self, animals_by_section_number: dict[int, int]
    ) -> list["Event"]:
        if self.state.transfer is None:
            raise DomainException("flock has not been transferred yet")

        if self.state.current_cycle != StallkarteCycle.FATTENING:
            raise DomainException("flock has not been transferred to fattening yet")

        if self.state.fattening_farm is None:
            raise DomainException("fattening farm is not assigned")

        for section in self.state.fattening_farm.sections:
            if section.number not in animals_by_section_number:
                raise DomainException(
                    f"number of animals for section {section.number} not provided"
                )
            if animals_by_section_number[section.number] < 0:
                raise DomainException(
                    f"number of animals for section {section.number} must be "
                    f"non-negative"
                )

        return [
            TransferDetailsRevised(
                animals_by_section=animals_by_section_number,
            ).event(),
        ]

    def record_ambient_climate(
        self,
        production_day: int,
        temperature_celsius: float | None,
        humidity_percent: float | None,
    ) -> list["Event"]:
        if production_day < 0:
            raise DomainException("production_day must be non-negative")

        return [
            AmbientClimateRecorded(
                production_day=production_day,
                temperature_celsius=temperature_celsius,
                humidity_percent=humidity_percent,
            ).event()
        ]

    def record_fattening_day_data(
        self,
        production_day: int,
        opening_time: str | None,
        weather_conditions: list[models.WeatherCondition],
        veterinarian: bool,
    ) -> list["Event"]:
        if production_day < 0:
            raise DomainException("production_day must be non-negative")

        transfer = self.state.transfer
        if transfer is None or production_day < transfer.production_day:
            raise DomainException(
                "fattening day data can only be recorded after transfer"
            )

        return [
            FatteningDayDataRecorded(
                production_day=production_day,
                opening_time=opening_time,
                weather_conditions=weather_conditions,
                veterinarian=veterinarian,
            ).event()
        ]

    def record_feed_consumption(
        self,
        production_day: int,
        amount_kg: float,
    ) -> list["Event"]:
        if production_day < 0:
            raise DomainException("production_day must be non-negative")

        return [
            FeedConsumptionRecorded(
                production_day=production_day,
                amount_kg=amount_kg,
            ).event()
        ]

    def record_water_consumption(
        self,
        production_day: int,
        amount_liters: float,
    ) -> list["Event"]:
        if production_day < 0:
            raise DomainException("production_day must be non-negative")

        return [
            WaterConsumptionRecorded(
                production_day=production_day,
                amount_liters=amount_liters,
            ).event()
        ]

    def record_weight(
        self,
        production_day: int,
        weight_grams: float,
    ) -> list["Event"]:
        if production_day < 0:
            raise DomainException("production_day must be non-negative")

        return [
            WeightRecorded(
                production_day=production_day, weight_grams=weight_grams
            ).event()
        ]

    def save_general_notes(
        self,
        production_day: int,
        general_notes: list[models.NoteEntry],
    ) -> list["Event"]:
        if production_day < 0:
            raise DomainException("production_day must be non-negative")

        return [
            GeneralNotesReplaced(
                production_day=production_day,
                general_notes=general_notes,
            ).event()
        ]

    def save_finish_notes(
        self,
        finish_notes: list[models.NoteEntry],
    ) -> list["Event"]:
        if self.state.is_finished:
            raise DomainException("stallkarte is already finished")

        return [
            FinishNotesReplaced(
                finish_notes=finish_notes,
            ).event()
        ]

    def record_mortality(
        self,
        production_day: int,
        section_number: int,
        natural_deaths: int | None,
        selective_deaths: int | None,
        shift: MortalityRecordedShift,
    ) -> list["Event"]:
        if production_day < 0:
            raise DomainException("production_day must be non-negative")

        if self.state.current_cycle_farm is None:
            raise DomainException("no farm assigned for the current cycle")

        section_exists = any(
            section.number == section_number
            for section in self.state.current_cycle_farm.sections
        )
        if not section_exists:
            raise DomainException(f"section number {section_number} does not exist")

        return [
            MortalityRecorded(
                production_day=production_day,
                section_number=section_number,
                natural_deaths=natural_deaths,
                selective_deaths=selective_deaths,
                shift=shift,
            ).event()
        ]

    def log_section_note(
        self,
        production_day: int,
        section_number: int,
        note: str,
    ) -> list["Event"]:
        if production_day < 0:
            raise DomainException("production_day must be non-negative")

        if self.state.current_cycle_farm is None:
            raise DomainException("no farm assigned for the current cycle")

        section_exists = any(
            section.number == section_number
            for section in self.state.current_cycle_farm.sections
        )
        if not section_exists:
            raise DomainException(f"section number {section_number} does not exist")

        return [
            SectionNoteLogged(
                production_day=production_day,
                section_number=section_number,
                note=note,
            ).event()
        ]

    def finish(
        self,
        date: datetime.date,
        finish_notes: list[models.NoteEntry] | None = None,
    ) -> list["Event"]:
        if self.state.is_finished:
            raise DomainException("stallkarte is already finished")

        resolved_finish_notes = finish_notes if finish_notes is not None else []
        return [
            Finished(
                date=date,
                finish_notes=resolved_finish_notes,
            ).event()
        ]

    def reopen(self) -> list["Event"]:
        if not self.state.is_finished:
            raise DomainException("stallkarte is not finished")

        return [Reopened().event()]

    def perform_alarm_test(
        self,
        cycle: StallkarteCycle,
        did_emergency_power_test: bool | None,
        did_alarm_test: bool | None,
    ) -> list["Event"]:
        return [
            AlarmTestPerformed(
                cycle=models.ChecklistCycle(cycle.value),
                did_emergency_power_test=did_emergency_power_test,
                did_alarm_test=did_alarm_test,
            ).event()
        ]

    def perform_lighting_program(
        self,
        cycle: StallkarteCycle,
        did_dark_period_test: bool | None,
        had_divergence_due_to_vet: bool | None,
    ) -> list["Event"]:
        return [
            LightingProgramPerformed(
                cycle=models.ChecklistCycle(cycle.value),
                did_dark_period_test=did_dark_period_test,
                had_divergence_due_to_vet=had_divergence_due_to_vet,
            ).event()
        ]

    def apply_pest_control_measures(
        self,
        cycle: StallkarteCycle,
        did_perform_pest_control: bool | None,
        annotation: str | None,
    ) -> list["Event"]:
        return [
            PestControlMeasuresApplied(
                cycle=models.ChecklistCycle(cycle.value),
                did_perform_pest_control=did_perform_pest_control,
                annotation=annotation,
            ).event()
        ]

    def clean_silo(
        self,
        cycle: StallkarteCycle,
        date: datetime.date | None,
        detergent: str | None,
        dosis: str | None,
    ) -> list["Event"]:
        return [
            SiloCleaned(
                cycle=models.ChecklistCycle(cycle.value),
                date=date,
                detergent=detergent,
                dosis=dosis,
            ).event()
        ]

    def disinfect_stable(
        self,
        cycle: StallkarteCycle,
        date: datetime.date | None,
        disinfectant: str | None,
        dosis: str | None,
    ) -> list["Event"]:
        return [
            StableDisinfected(
                cycle=models.ChecklistCycle(cycle.value),
                date=date,
                disinfectant=disinfectant,
                dosis=dosis,
            ).event()
        ]

    def disinfect_water_line(
        self,
        cycle: StallkarteCycle,
        date: datetime.date | None,
        disinfectant: str | None,
        dosis: str | None,
    ) -> list["Event"]:
        return [
            WaterLineDisinfected(
                cycle=models.ChecklistCycle(cycle.value),
                date=date,
                disinfectant=disinfectant,
                dosis=dosis,
            ).event()
        ]
