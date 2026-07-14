from app.domain.stallkarte.event import EventPayload
from app.domain.stallkarte.events.models import SectionInstallationDetails


class InstallationDetailsReplaced(
    EventPayload, event_type="stallkarte.installation_details_replaced"
):
    section_details: list[SectionInstallationDetails]
