from .agriculturalholding import AgriculturalHolding

# noinspection PyShadowingBuiltins
from .exception import DomainException as Exception
from .farm import Farm, FarmType
from .section import Section
from .chicken_breed import ChickenBreed
from .shallow_stallkarte import ShallowStallkarte
from .stallkarte import (
    Stallkarte,
    StallkarteAggregator,
    StallkarteAlarmTest,
    StallkarteChecklist,
    StallkarteCycle,
    StallkarteEvent,
    StallkarteFarm,
    StallkarteLightingProgram,
    StallkartePestControlMeasures,
    StallkarteSection,
    StallkarteSiloCleaned,
    StallkarteStableDisinfected,
    StallkarteState,
    StallkarteStateDay,
    StallkarteStateDaySection,
    StallkarteTransfer,
    StallkarteWaterLineDisinfected,
)
from .user import User

# Rebuild models to ensure all fields and references are properly initialized.
# This is required since the model definitions are defined without importing any
# referenced models to prevent circular dependencies (e.g. holding -> farm -> holding).
# Now they are all loaded, so pydantic can resolve all references.
User.model_rebuild()
AgriculturalHolding.model_rebuild()
Farm.model_rebuild()
Section.model_rebuild()
Stallkarte.model_rebuild()

__all__ = [
    "AgriculturalHolding",
    "Exception",
    "Farm",
    "FarmType",
    "Section",
    "ShallowStallkarte",
    "Stallkarte",
    "StallkarteAggregator",
    "StallkarteAlarmTest",
    "StallkarteChecklist",
    "StallkarteCycle",
    "StallkarteEvent",
    "StallkarteFarm",
    "StallkarteLightingProgram",
    "StallkartePestControlMeasures",
    "StallkarteSection",
    "StallkarteSiloCleaned",
    "StallkarteStableDisinfected",
    "StallkarteState",
    "StallkarteStateDay",
    "StallkarteStateDaySection",
    "StallkarteTransfer",
    "StallkarteWaterLineDisinfected",
    "User",
    "ChickenBreed",
]
