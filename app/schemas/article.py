from datetime import datetime

from pydantic import BaseModel

from app.models.enums import Languages
from app.schemas.base import TranslatableModel
from .city import City
from .docs import DocFile


class ArticleTranslationCreate(BaseModel):
    name: str
    description: str
    content: str
    language: Languages


class ArticleCreate(BaseModel):
    name: str
    description: str
    content: str
    photo_id: int | None
    city_id: int | None
    translations: list[ArticleTranslationCreate]


class Article(TranslatableModel):
    id: int
    name: str
    content: str
    description: str
    city: City | None
    created_at: datetime | None
    photo: DocFile | None

    class Config:
        orm_mode = True


class ArticleResponse(BaseModel):
    total: int
    data: list[Article]
