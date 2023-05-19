from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel

from app.models import enums
from .base import TranslatableModel
from .bed_type import BedType
from .docs import PhotoObject, PhotoCreate
from .service import ServiceCategory


class RoomType(TranslatableModel):
    id: int
    type: str


class RoomName(TranslatableModel):
    id: int
    name: str


class PriceForLessPeople(BaseModel):
    number_of_people: int
    discount_unit: enums.BillingUnit
    discount_amount: float
    is_active: bool


class RoomStatus(BaseModel):
    id: int
    property_room_id: int
    booked_room_id: int | None = None
    status: enums.RoomStatus
    status_from: date | None = None
    status_until: date | None = None
    is_disabled: bool | None = None

    class Config:
        orm_mode = True


class Room(BaseModel):
    id: int
    name: str
    status: enums.RoomStatus

    class Config:
        orm_mode = True


class RoomTemplate(TranslatableModel):
    id: int
    property_id: int
    type: RoomType
    name: RoomName
    number_of_rooms: int = 1
    max_number_of_guests: int = 1
    max_number_of_children: int = 0
    area: float
    pets_allowed: bool = False
    smoking_allowed: bool | None = None

    price: float
    price_has_discount: bool = False
    price_discount_unit: enums.BillingUnit | None = None
    price_discount_amount: float = 0.0
    price_discount_from: datetime | None = None
    price_discount_until: datetime | None = None

    price_for_resident: float
    price_for_resident_has_discount: bool = False
    price_for_resident_discount_unit: enums.BillingUnit | None = None
    price_for_resident_discount_amount: float = 0.0
    price_for_resident_discount_from: datetime | None = None
    price_for_resident_discount_until: datetime | None = None

    price_for_less_people: list[PriceForLessPeople] = []
    price_for_resident_less_people: list[PriceForLessPeople] = []

    beds: list[RoomTemplateBed] = []
    photos: list[PhotoObject] = []


class RoomTemplateWithRooms(RoomTemplate):
    rooms: list[Room] = []


class RoomTemplateCreate(BaseModel):
    type_id: int
    name_id: int
    number_of_rooms: int
    max_number_of_guests: int
    max_number_of_children: int
    area: float
    pets_allowed: bool = False
    smoking_allowed: bool | None = None

    price: float
    price_has_discount: bool = False
    price_discount_unit: enums.BillingUnit = None
    price_discount_amount: float | None = 0.0
    price_discount_from: datetime | None = None
    price_discount_until: datetime | None = None

    price_for_resident: float
    price_for_resident_has_discount: bool = False
    price_for_resident_discount_unit: enums.BillingUnit = None
    price_for_resident_discount_amount: float | None = 0.0
    price_for_resident_discount_from: datetime | None = None
    price_for_resident_discount_until: datetime | None = None

    price_for_less_people: list[PriceForLessPeople] = []
    price_for_resident_less_people: list[PriceForLessPeople] = []

    beds: list[RoomBedCreate]
    photos: list[PhotoCreate]
    services: list[int]
    numbers: list[str]


class RoomTemplateUpdate(BaseModel):
    type_id: int
    name_id: int
    number_of_rooms: int
    max_number_of_guests: int
    max_number_of_children: int
    area: float
    pets_allowed: bool = False
    smoking_allowed: bool | None = None

    price: float
    price_has_discount: bool = False
    price_discount_unit: enums.BillingUnit = None
    price_discount_amount: float | None = 0.0
    price_discount_from: datetime | None = None
    price_discount_until: datetime | None = None

    price_for_resident: float
    price_for_resident_has_discount: bool = False
    price_for_resident_discount_unit: enums.BillingUnit = None
    price_for_resident_discount_amount: float | None = 0.0
    price_for_resident_discount_from: datetime | None = None
    price_for_resident_discount_until: datetime | None = None

    price_for_less_people: list[PriceForLessPeople] = []
    price_for_resident_less_people: list[PriceForLessPeople] = []

    beds: list[RoomBedCreate]
    photos: list[PhotoCreate]
    numbers: list[str]


class RoomTemplateBed(BaseModel):
    id: int
    bed_type: BedType
    number_of_beds: int

    class Config:
        orm_mode = True


class RoomStatusUpdate(BaseModel):
    status: enums.RoomStatus


class RoomStatusByDay(BaseModel):
    for_delete: bool = False
    status_from: date


class RoomNumberUpdate(BaseModel):
    name: str


class RoomBedUpdate(BaseModel):
    id: int
    bed_type_id: int
    number_of_beds: int


class RoomBedCreate(BaseModel):
    bed_type_id: int
    number_of_beds: int


class RoomServiceObj(TranslatableModel):
    id: int
    category: ServiceCategory | None
    service_name: str
