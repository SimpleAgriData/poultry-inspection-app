from sqlalchemy.orm import Session

from app.services.database.repositories import (
    AgriculturalHoldingRepository,
    FarmRepository,
    SectionRepository,
    StallkarteRepository,
)


class Database:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.agricultural_holding_repository = AgriculturalHoldingRepository(session)
        self.farm_repository = FarmRepository(session)
        self.section_repository = SectionRepository(session)
        self.stallkarte_repository = StallkarteRepository(session)
