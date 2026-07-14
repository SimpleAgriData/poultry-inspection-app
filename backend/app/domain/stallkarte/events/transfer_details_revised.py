from app.domain.stallkarte.event import EventPayload

type SectionNumber = int


class TransferDetailsRevised(
    EventPayload, event_type="stallkarte.transfer_details_revised"
):
    animals_by_section: dict[SectionNumber, int]
