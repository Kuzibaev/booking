import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import TranslationBase, Base
from app.models.enums import RoomStatus, BillingUnit


class RoomType(Base):
    type = sa.Column(sa.String, nullable=False)
    max_number_of_guests = sa.Column(sa.Integer, default=1, nullable=False)
    translations = relationship("RoomTypeTranslation", back_populates="room_type", lazy="selectin")
    room_names = relationship("RoomName", back_populates="type", lazy="selectin")
    rooms = relationship("PropertyRoomTemplate", back_populates="type", lazy="noload")

    def __repr__(self):
        return self.type

    def __str__(self):
        return self.__repr__()


class RoomName(Base):
    type_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("room_type.id", ondelete='CASCADE'),
        nullable=False
    )
    type = relationship("RoomType", lazy="noload")
    name = sa.Column(sa.String, nullable=False)

    translations = relationship("RoomNameTranslation", back_populates="room_name", lazy="selectin")

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()


class PropertyRoomTemplate(Base):
    property_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("property.id", ondelete='CASCADE'),
        nullable=False
    )
    property = relationship("Property", back_populates="rooms", lazy="noload")
    type_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("room_type.id", ondelete='CASCADE'),
        nullable=False
    )
    type = relationship("RoomType", back_populates="rooms", lazy="joined")
    name_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("room_name.id", ondelete='CASCADE'),
        nullable=False
    )

    name = relationship("RoomName", lazy="joined")
    number_of_rooms = sa.Column(sa.Integer, default=1, nullable=False)
    max_number_of_guests = sa.Column(sa.Integer, default=1, nullable=False)
    max_number_of_children = sa.Column(sa.Integer, default=0, nullable=False)
    area = sa.Column(sa.Float, default=0, nullable=False)
    pets_allowed = sa.Column(sa.Boolean, default=False, nullable=True)
    smoking_allowed = sa.Column(sa.Boolean, nullable=True)

    price = sa.Column(sa.Float(precision=10, decimal_return_scale=2), nullable=False)
    price_has_discount = sa.Column(sa.Boolean, default=False, nullable=False)
    price_discount_unit = sa.Column(sa.Enum(BillingUnit), nullable=True)
    price_discount_amount = sa.Column(sa.Float, nullable=False, default=0)
    price_discount_from = sa.Column(sa.DateTime(timezone=True), nullable=True)
    price_discount_until = sa.Column(sa.DateTime(timezone=True), nullable=True)

    price_for_resident = sa.Column(sa.Float(precision=10, decimal_return_scale=2), nullable=False)
    price_for_resident_has_discount = sa.Column(sa.Boolean, default=False, nullable=False)
    price_for_resident_discount_unit = sa.Column(sa.Enum(BillingUnit), nullable=True)
    price_for_resident_discount_amount = sa.Column(sa.Float, nullable=False, default=0)
    price_for_resident_discount_from = sa.Column(sa.DateTime(timezone=True), nullable=True)
    price_for_resident_discount_until = sa.Column(sa.DateTime(timezone=True), nullable=True)

    price_for_less_people = sa.Column(JSONB, default=[], nullable=False)
    price_for_resident_less_people = sa.Column(JSONB, default=[], nullable=False)

    is_deleted = sa.Column(sa.Boolean, default=False, nullable=False)

    beds = relationship("RoomBed", back_populates="room", lazy="selectin")
    photos = relationship("RoomPhoto", back_populates="room", lazy="selectin")
    services = relationship("RoomService", back_populates="room", lazy="noload")
    rooms = relationship("PropertyRoom", back_populates="room", lazy="selectin")

    def __repr__(self):
        return f"RoomTemplate id={self.id}"

    def __str__(self):
        return self.__repr__()


class RoomService(Base):
    room_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("property_room_template.id", ondelete='CASCADE'),
        nullable=False
    )
    service_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("service.id", ondelete='CASCADE'),
        nullable=False
    )
    room = relationship("PropertyRoomTemplate", back_populates='services')
    service = relationship("Service", lazy='selectin')


class RoomPhoto(Base):
    photo_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("doc_file.id"))
    room_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("property_room_template.id", ondelete='CASCADE'),
        nullable=False
    )
    is_default: bool = False
    photo = relationship("DocFile", lazy='selectin')
    room = relationship("PropertyRoomTemplate", back_populates="photos")


class RoomBed(Base):
    bed_type_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("bed_type.id", ondelete='CASCADE'),
        nullable=False
    )
    room_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("property_room_template.id", ondelete='CASCADE'),
        nullable=False
    )
    room = relationship("PropertyRoomTemplate", back_populates="beds")
    bed_type = relationship("BedType", lazy='selectin')
    number_of_beds = sa.Column(sa.Integer, nullable=False, default=1)


class PropertyRoomStatus(Base):
    property_room_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("property_room.id", ondelete='CASCADE')
    )
    booked_room_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("booked_room.id", ondelete='CASCADE'),
        nullable=True
    )
    status = sa.Column(sa.Enum(RoomStatus), default=RoomStatus.EMPTY)
    status_from = sa.Column(sa.Date, nullable=True)
    status_until = sa.Column(sa.Date, nullable=True)
    is_disabled = sa.Column(sa.Boolean, default=True, nullable=True)
    booked_room = relationship("BookedRoom", lazy='noload')
    room = relationship("PropertyRoom", back_populates="statuses", lazy="noload")


class PropertyRoom(Base):
    room_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('property_room_template.id', ondelete='CASCADE'),
        nullable=False
    )
    name = sa.Column(sa.String, nullable=False)
    status = sa.Column(sa.Enum(RoomStatus), default=RoomStatus.EMPTY)
    room = relationship("PropertyRoomTemplate", back_populates="rooms", lazy="noload")
    statuses = relationship("PropertyRoomStatus", back_populates="room", lazy="noload")

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()


class RoomTypeTranslation(TranslationBase):
    room_type = relationship("RoomType", back_populates="translations")
    room_type_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("room_type.id", ondelete='CASCADE'),
        nullable=False
    )
    type = sa.Column(sa.String, nullable=False)


class RoomNameTranslation(TranslationBase):
    room_name = relationship("RoomName", back_populates="translations")
    room_name_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("room_name.id", ondelete='CASCADE'),
        nullable=False
    )
    name = sa.Column(sa.String, nullable=False)
