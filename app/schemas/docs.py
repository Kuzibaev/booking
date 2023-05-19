from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Extra, Field

from ._config import PhotoGetter


class DocFile(BaseModel):
    id: UUID
    type: str
    created_at: datetime
    updated_at: datetime | None
    url: str

    class Config:
        orm_mode = True
        getter_dict = PhotoGetter
        extra = Extra.allow


class DocFileCreate(BaseModel):
    name: str
    type: str
    path: str


class DocFileUpdate(BaseModel):
    pass


class Photo(DocFile):
    is_default: bool = False


class PhotoCreate(BaseModel):
    photo_id: UUID
    is_default: bool = Field(default=False)


class PhotoObject(BaseModel):
    id: int
    photo: Photo
    is_default: bool = False

    class Config:
        orm_mode = True
