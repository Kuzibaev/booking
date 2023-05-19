from typing import Any

from pydantic import BaseModel

from .base import TranslatableModel


class AboutUs(TranslatableModel):
    id: int
    text: str
    phone: str
    email: str
    address: str
    latitude: float
    longitude: float

    class Config:
        orm_mode = True


class AboutUsCreate(BaseModel):
    pass


class Faq(TranslatableModel):
    question: str
    answer: str

    class Config:
        orm_mode = True


class FaqTranslationCreate(BaseModel):
    language: Any
    is_default: bool = False
    question: str
    answer: str


class FaqCreate(BaseModel):
    question: str
    answer: str
    translations: list[FaqTranslationCreate]


class FaqUpdate(BaseModel):
    question: str | None
    answer: str | None
