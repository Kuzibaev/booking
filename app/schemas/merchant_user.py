from uuid import UUID

from pydantic import BaseModel, Field

from app.models import enums
from app.models.enums import MerchantUserRole
from app.schemas.base import PhoneNumber
from app.schemas.user import Photo


class Dashboard(BaseModel):
    id: int
    title: str | None = None
    balance: float
    is_active: bool
    default_property_id: int | None = None

    class Config:
        orm_mode = True


class MerchantUser(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone: PhoneNumber
    dashboard: Dashboard
    photo: Photo | None = None

    class Config:
        orm_mode = True


class PersonalUser(MerchantUser):
    email: str | None = None
    address: str | None = None


class PersonalUserCreate(BaseModel):
    first_name: str
    last_name: str
    phone: PhoneNumber
    password: str
    address: str
    photo_id: UUID | None = None
    email: str | None = None


class PersonalUserUpdate(BaseModel):
    first_name: str
    last_name: str
    new_password: str
    email: str
    address: str
    phone: PhoneNumber
    photo_id: UUID | None = None


class MerchantUserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    old_password: str = ''
    new_password: str | None = None
    photo_id: UUID | None = None


class MerchantUserResetPassword(BaseModel):
    token: str
    code: str
    new_password: str = Field(...)
    new_password2: str = Field(...)
