from pydantic import BaseModel

class ChickenBreed(BaseModel):
    id: int
    label: str
    description: str
