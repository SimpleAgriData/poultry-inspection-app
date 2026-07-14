"""
This module holds all events related to the Stallkarte domain. The events cover various
aspects of the Stallkarte lifecycle, including daily events, farm assignments, animal
transfers, and the start and finish of the Stallkarte.
"""

from .checklistevents import (
    AlarmTestPerformed,
    LightingProgramPerformed,
    PestControlMeasuresApplied,
    SiloCleaned,
    StableDisinfected,
    WaterLineDisinfected,
)
from .dailyevents import (
    AmbientClimateRecorded,
    FatteningDayDataRecorded,
    FeedConsumptionRecorded,
    GeneralNotesReplaced,
    MortalityRecorded,
    SectionNoteLogged,
    WaterConsumptionRecorded,
    WeightRecorded,
)
from .details_revised import DetailsRevised
from .fattening_farm_assigned import FatteningFarmAssigned
from .finish_notes_replaced import FinishNotesReplaced
from .finished import Finished
from .flock_transferred import FlockTransferred
from .installation_details_replaced import InstallationDetailsReplaced
from .rearing_farm_assigned import RearingFarmAssigned
from .reopened import Reopened
from .stallkarte_started import StallkarteStarted
from .transfer_details_revised import TransferDetailsRevised

__all__ = [
    "AlarmTestPerformed",
    "AmbientClimateRecorded",
    "DetailsRevised",
    "FatteningDayDataRecorded",
    "FatteningFarmAssigned",
    "FeedConsumptionRecorded",
    "FinishNotesReplaced",
    "Finished",
    "FlockTransferred",
    "GeneralNotesReplaced",
    "InstallationDetailsReplaced",
    "LightingProgramPerformed",
    "MortalityRecorded",
    "PestControlMeasuresApplied",
    "RearingFarmAssigned",
    "Reopened",
    "SectionNoteLogged",
    "SiloCleaned",
    "StableDisinfected",
    "StallkarteStarted",
    "TransferDetailsRevised",
    "WaterConsumptionRecorded",
    "WaterLineDisinfected",
    "WeightRecorded",
]
