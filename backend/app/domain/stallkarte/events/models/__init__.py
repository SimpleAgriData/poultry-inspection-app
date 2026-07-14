"""
This module holds structures that are used in different events. It is a deliberate
decision to use these structures instead of already existing models from the Stallkarte
domain, since changes made there should not affect historical events. The models in
this module are strictly bound to the events they are used in.
"""

from .assigned_farm import AssignedFarmSection, AssignedFarmType
from .cycle import ChecklistCycle
from .installation_details import ParentFlockEntry, SectionInstallationDetails
from .note_event import (
    NoteEntry,
    NoteType,
    SockTestResult,
    TreatmentAmountUnit,
    TreatmentCode,
    VaccinationCode,
    WaitingTimeUnit,
)
from .weather_condition import WeatherCondition

__all__ = [
    "AssignedFarmSection",
    "AssignedFarmType",
    "ChecklistCycle",
    "NoteEntry",
    "NoteType",
    "ParentFlockEntry",
    "SectionInstallationDetails",
    "SockTestResult",
    "TreatmentAmountUnit",
    "TreatmentCode",
    "VaccinationCode",
    "WaitingTimeUnit",
    "WeatherCondition",
]
