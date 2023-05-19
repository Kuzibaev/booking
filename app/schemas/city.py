from pydantic import BaseModel

from .base import TranslatableModel
from app.models.enums import Languages


class CityTranslationCreate(BaseModel):
    name: str
    language: Languages


class CityCreate(BaseModel):
    name: str
    name_slug: str
    latitude: float
    longitude: float
    translations: list[CityTranslationCreate]


class City(TranslatableModel):
    id: int
    name: str
    name_slug: str
    latitude: float
    longitude: float

    class Config:
        orm_mode = True


class CitySearch(BaseModel):
    id: int
    type: str
    name: str
    name_slug: str
    hotels: int = None
