from datetime import date

from pydantic import BaseModel
from uuid import UUID

from app.models.enums import Gender
from app.models.enums import Languages
from .docs import DocFile
from .oauth import OAuthUserDataResponseSchema


class Photo(DocFile):
    pass


class UserBase(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    gender: Gender | None = None
    birthday: date | None = None
    language: Languages


class UserCreate(UserBase):
    phone: str


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    gender: Gender | None = None
    birthday: date | None = None
    photo_id: UUID | None = None
    language: Languages | None = None


class User(UserUpdate):
    id: int
    photo: Photo | None
    phone: str | None
    social_accounts: list[OAuthUserDataResponseSchema] = []

    class Config:
        orm_mode = True
