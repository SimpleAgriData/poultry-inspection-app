from pydantic import BaseModel, ConfigDict
from sqlalchemy import select

from app import domain
from app.db import models
from app.services.database.repositories.repository import Repository
from app.services.database.translate import translate

class ChickenBreedRepository(Repository):
    def get_all_breeds(self) -> list[domain.ChickenBreed]:
        statement = select(models.ChickenBreed)
        db_breeds = self.session.execute(statement).scalars().all()
        return [translate.chicken_breed_to_domain(breed) for breed in db_breeds]