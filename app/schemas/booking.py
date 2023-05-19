from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, validator, Extra

from app.models.enums import BookingStatus, BookingCanceledBy
from .base import TranslatableModel
from .city import City
from .docs import Photo
from .property import PropertyType
from .property_room import RoomStatus, RoomTemplate, Room
from .reviews import ReviewQuestionAnswer
from ..models import enums


class BedType(BaseModel):
    id: int
    type: str

    class Config:
        orm_mode = True


class BookingCreate(BaseModel):
    property_id: int
    name: str
    booked_from: datetime
    booked_to: datetime
    rooms: list[BookedRoomCreate]


class BookedRoomCreate(BaseModel):
    room_id: int
    bed_type_id: int
    bed_for_children: bool = False
    number_of_people: int = 1
    for_resident: bool = False


class BookingUpdate(BaseModel):
    name: str
    booked_from: datetime
    booked_to: datetime
    rooms: list[BookedRoomCreate]


class BookedRoomBed(BaseModel):
    id: int
    bed_type: BedType
    number_of_beds: int
    bed_for_children: bool = False

    class Config:
        orm_mode = True


class BookedRoom(BaseModel):
    id: int
    booked_from: datetime
    booked_to: datetime
    count: int = 0
    property_room_template_id: int
    property_room: Room | None = None
    price: float
    for_resident: bool = False
    number_of_people: int
    status: BookingStatus
    room: RoomTemplate
    beds: list["BookedRoomBed"] = []

    class Config:
        orm_mode = True


class PropertyAddress(TranslatableModel):
    id: int
    type: PropertyType
    name: str
    description: str
    address: str
    city: City
    star_rating: enums.PropertyStarRating

    latitude: float
    longitude: float

    checkin_from: datetime | None
    checkout_from: datetime | None

    photos: list[Photo] = []

    class Config:
        orm_mode = True


class RoomPhoto(BaseModel):
    id: int
    photo: Photo

    class Config:
        orm_mode = True


class BookingUser(BaseModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    phone: str

    class Config:
        orm_mode = True


class Booking(BaseModel):
    id: int
    name: str
    user: BookingUser
    booked_from: datetime
    booked_to: datetime

    is_arrived: bool = False
    total_number_of_people: int = 0
    total_price: float = 0

    status: BookingStatus
    property: PropertyAddress
    created_at: datetime
    rooms: list[BookedRoom]

    class Config:
        orm_mode = True


class BedTypeHistory(BaseModel):
    id: int
    type: str

    class Config:
        orm_mode = True


class BookedRoomBedHistory(BaseModel):
    id: int
    bed_type: BedTypeHistory
    number_of_beds: int
    bed_for_young_children: bool = False

    class Config:
        orm_mode = True


class BookedRoomHistory(BaseModel):
    id: int
    property_room_template_id: int
    count: int | None
    price: float
    status: BookingStatus
    room: RoomTemplate
    beds: list["BookedRoomBedHistory"] = []

    class Config:
        orm_mode = True


class BookingReview(BaseModel):
    property_id: int
    avg: float

    class Config:
        orm_mode = True


class BookingComment(BaseModel):
    id: int
    comment: str
    avg: float

    class Config:
        orm_mode = True


class BookingHistory(TranslatableModel):
    id: int
    name: str
    user: BookingUser
    property: PropertyAddress
    total_price: float
    total_number_of_people: int
    booked_from: datetime
    booked_to: datetime
    status: BookingStatus
    canceled_by: BookingCanceledBy | None = None
    reason_of_cancellation: str | None = None
    rooms: list[BookedRoomHistory] = []
    reviews: list[ReviewQuestionAnswer] = []
    comment: BookingComment | None = None

    class Config:
        orm_mode = True


class PropertyOrderDetail(BaseModel):
    id: int
    checkin_from: datetime | None
    checkin_until: datetime | None
    checkout_from: datetime | None
    checkout_until: datetime | None

    class Config:
        orm_mode = True


class PropertyHistoryOfBooking(BaseModel):
    name: str

    property: PropertyOrderDetail

    class Config:
        orm_mode = True


class PropertyRoomWithStatus(BaseModel):
    id: int
    room_id: int
    name: str
    room_status: RoomStatus

    class Config:
        orm_mode = True


class PropertyRoomTemplateWithRooms(RoomTemplate):
    rooms: list[PropertyRoomWithStatus] = []

    class Config:
        orm_mode = True


class PropertyHistoryOfBookings(BaseModel):
    id: int
    booking_id: int
    booking: PropertyHistoryOfBooking
    price: float
    status: BookingStatus
    room: RoomTemplate

    class Config:
        orm_mode = True


class AcceptOrderWithRoom(BaseModel):
    booked_room_id: int
    room_id: int
