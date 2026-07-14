from app.domain.stallkarte.event import EventPayload
from app.domain.stallkarte.events import models


class RearingFarmAssigned(EventPayload, event_type="stallkarte.rearing_farm_assigned"):
    farm_id: int
    farm_name: str
    farm_type: models.AssignedFarmType
    farm_vvvo_number: str
    sections: list[models.AssignedFarmSection]
