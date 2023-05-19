import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship

from .base import Base
from .enums import BookingStatus, BookingCanceledBy


class Booking(Base):
    name = sa.Column(sa.String, nullable=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'), nullable=False)
    property_id = sa.Column(sa.Integer, sa.ForeignKey('property.id'), nullable=False)

    booked_from = sa.Column(sa.DateTime(timezone=True), nullable=False)
    booked_to = sa.Column(sa.DateTime(timezone=True), nullable=False)

    total_price = sa.Column(sa.Float(precision=10, decimal_return_scale=2), nullable=False, default=0)
    total_number_of_people = sa.Column(sa.Integer, default=1, nullable=False)

    status = sa.Column(sa.Enum(BookingStatus), nullable=False, default=BookingStatus.PENDING)

    is_arrived = sa.Column(sa.Boolean, default=False, nullable=False)
    reason_of_cancellation = sa.Column(sa.Text, nullable=True)
    canceled_by = sa.Column(sa.Enum(BookingCanceledBy), nullable=True)

    user = relationship("User", back_populates="bookings", lazy="selectin")
    property = relationship("Property", back_populates="bookings", lazy="selectin")
    rooms = relationship("BookedRoom", lazy="selectin")
    reviews = relationship("ReviewQuestionAnswer", back_populates="booking", lazy="selectin")
    comment = relationship("UserComment", back_populates="booking", lazy="selectin", uselist=False)


class BookedRoom(Base):
    booking_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("booking.id", ondelete='CASCADE'),
        nullable=False
    )
    booking = relationship('Booking', back_populates='rooms', lazy="noload")
    booked_from = sa.Column(sa.DateTime(timezone=True), nullable=False)
    booked_to = sa.Column(sa.DateTime(timezone=True), nullable=False)
    property_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('property.id'),
        nullable=False
    )
    property_room_template_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("property_room_template.id", ondelete='SET NULL'),
        nullable=False,
    )
    property_room_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('property_room.id', ondelete='SET NULL'),
        nullable=True
    )
    status = sa.Column(ENUM(BookingStatus), nullable=False, default=BookingStatus.PENDING)
    number_of_people = sa.Column(sa.Integer, default=1, nullable=False)
    reason_of_cancellation = sa.Column(sa.Text, nullable=True)
    canceled_by = sa.Column(sa.Enum(BookingCanceledBy), nullable=True)

    for_resident = sa.Column(sa.Boolean, default=False)
    price = sa.Column(sa.Float(precision=10, decimal_return_scale=2), nullable=False)

    property = relationship("Property", lazy="selectin")
    room = relationship("PropertyRoomTemplate", lazy="selectin")
    property_room = relationship("PropertyRoom", lazy="selectin")
    beds = relationship("BookedRoomBed", lazy="selectin")

    def __repr__(self):
        return f'BookedRoom id {self.id}'

    def __str__(self):
        return f'BookedRoom id {self.id}'


class BookedRoomBed(Base):
    booked_room_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("booked_room.id", ondelete='CASCADE'),
        nullable=False
    )
    bed_for_children = sa.Column(sa.Boolean, default=False)
    bed_type_id = sa.Column(sa.Integer, sa.ForeignKey("bed_type.id"), nullable=False)
    number_of_beds = sa.Column(sa.Integer, default=1, nullable=False)

    booked_room = relationship("BookedRoom", back_populates="beds")
    bed_type = relationship("BedType", lazy='joined')
