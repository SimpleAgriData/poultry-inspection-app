"""
The Stallkarte domain is built around an event-sourcing architecture. This module
serves as the central hub for all components related to the Stallkarte domain, including
events, state representations, and the aggregator responsible for processing events
to maintain the current state of the Stallkarte.
"""

from .apply import StallkarteAggregator
from .event import Event as StallkarteEvent
from .parse_event import parse_event
from .stallkarte import Stallkarte
from .stallkarte_state import (
    StallkarteAlarmTest,
    StallkarteChecklist,
    StallkarteCycle,
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

__all__ = [
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
    "parse_event",
]
