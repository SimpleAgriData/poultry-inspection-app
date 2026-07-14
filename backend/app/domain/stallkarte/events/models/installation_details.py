from pydantic import BaseModel


class ParentFlockEntry(BaseModel):
    herd_identifier: str
    production_week: int


class SectionInstallationDetails(BaseModel):
    section_number: int
    initial_animals_count: int
    initial_weight_grams: float
    bedding: str
    parent_flocks: list[ParentFlockEntry]
