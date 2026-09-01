
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.db.models import ChickenBreed
from app.db import get_engine
from app.db.models.mixins import Base

def init_database(settings)->None:
    engine = get_engine(settings.db.url)
    
    Base.metadata.create_all(engine)
    seed_database(engine)

def seed_database(engine) -> None:
    with Session(engine) as session:
        existing = session.scalar(
            select(ChickenBreed).where(
                ChickenBreed.label == "ISA-JA-757"
            )
        )

        if existing is None:
            session.add(
                ChickenBreed(
                    label="ISA-JA-757",
                    description="The default chicken breed for organic chicken farming."
                )
            )
            session.commit()
