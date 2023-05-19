from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.models import enums
from .base import TranslatableModel, PhoneNumber
from .city import City
from .docs import Photo, PhotoCreate
from .language import Language
from .property_room import RoomTemplate, RoomTemplateCreate
from .user import UserBase


class PropertyType(TranslatableModel):
    id: int
    type: str


class PropertyServiceObj(TranslatableModel):
    id: int
    service_name: str

    class Config:
        orm_mode = True


class PropertyLanguage(BaseModel):
    id: int
    property_id: int
    language: Language

    class Config:
        orm_mode = True


class PropertyService(BaseModel):
    id: int
    icon: Photo | None
    service: PropertyServiceObj | None

    class Config:
        orm_mode = True


class PropertyRating(BaseModel):
    avg: float = 0

    class Config:
        orm_mode = True


class PropertyEasy(TranslatableModel):
    id: int
    type: PropertyType
    name: str
    is_active: enums.PropertyStatus


class Property(TranslatableModel):
    id: int
    type: PropertyType
    name: str
    author_name: str | None = None
    description: str
    website: str | None
    phone: str | None
    address: str
    latitude: float
    longitude: float
    city: City

    is_breakfast_served: bool
    is_breakfast_included_in_price: bool

    airport_distance: int | None
    city_centre_distance: int | None
    railway_distance: int | None

    star_rating: enums.PropertyStarRating
    total_number_of_rooms: int

    minimum_price_per_night: float
    minimum_price_per_night_for_resident: float

    checkin_from: datetime | None
    checkin_until: datetime | None
    checkout_from: datetime | None
    checkout_until: datetime | None

    pets_allowed: bool
    smoking_allowed: bool

    rooms: list[RoomTemplate] = []
    photos: list[Photo] = []
    services: list[PropertyService] = []
    languages: list[PropertyLanguage] = []
    rating: PropertyRating | None

    class Config:
        orm_mode = True


class PropertyTranslationCreate(BaseModel):
    language: str
    description: str
    address: str


class PropertyServiceCreate(BaseModel):
    service_id: int
    service_name: str


class PropertyCreate(BaseModel):
    name: str
    description: str
    type_id: int
    author_name: str | None
    website: str | None
    phone: PhoneNumber | None

    address: str
    city_id: int
    latitude: float
    longitude: float

    is_breakfast_served: bool
    is_breakfast_included_in_price: bool

    airport_distance: float | None
    city_centre_distance: float | None
    railway_distance: float | None

    star_rating: str
    total_number_of_rooms: int

    minimum_price_per_night: float
    minimum_price_per_night_for_resident: float

    checkin_from: datetime | None
    checkin_until: datetime | None
    checkout_from: datetime | None
    checkout_until: datetime | None

    pets_allowed: bool
    smoking_allowed: bool

    translations: list[PropertyTranslationCreate]
    photos: list[PhotoCreate]
    services: list[PropertyServiceCreate]
    rooms: list[RoomTemplateCreate]
    languages: list[int]


class PropertyReviewComment(BaseModel):
    id: int
    user: UserBase
    comment: str

    class Config:
        orm_mode = True


class PropertyUpdate(BaseModel):
    pass


class PropertySearch(BaseModel):
    id: int
    type: str
    name: str
    description: str
    city_slug: str


class SavedFilter(TranslatableModel):
    name: str
    price_gte: float
    price_lte: float
    property_types: list[int]
    city_centre_distances: list[float]
    ratings: list[float]
    other_filters: Any = None

    class Config:
        orm_mode = True


class BaseRoomName(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class BaseRoomType(BaseModel):
    id: int
    type: str
    max_number_of_guests: int = 1
    room_names: list[BaseRoomName]

    class Config:
        orm_mode = True


class PropertyPhoto(BaseModel):
    id: int
    photo: Photo

    class Config:
        orm_mode = True


class PropertySettings(TranslatableModel):
    id: int
    type: PropertyType
    name: str
    author_name: str | None = None
    description: str
    website: str | None
    phone: str | None
    address: str

    latitude: float
    longitude: float
    city: City
    star_rating: enums.PropertyStarRating

    checkin_from: datetime
    checkin_until: datetime
    checkout_from: datetime
    checkout_until: datetime
    translations: list = []

    class Config:
        orm_mode = True


class PropertySettingsUpdate(BaseModel):
    type_id: int
    name: str
    description: str
    city_id: int

    phone: str | None

    latitude: float
    longitude: float

    star_rating: enums.PropertyStarRating

    checkin_from: datetime
    checkin_until: datetime
    checkout_from: datetime
    checkout_until: datetime

    translations: list[PropertyTranslationCreate]
