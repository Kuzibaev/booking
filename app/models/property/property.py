import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship

from app.core.logging import app_logger
from app.models.base import Base, TranslationBase
from app.models.enums import PropertyStarRating, PropertyStatus


class PropertyType(Base):
    type = sa.Column(sa.String, nullable=False)

    translations = relationship("PropertyTypeTranslation", backref="property_type", lazy="selectin")
    properties = relationship("Property", back_populates="type", lazy="noload")

    def __repr__(self):
        return f"PropertyType id={self.id}"

    def __str__(self):
        return self.type


class Property(Base):
    type = relationship("PropertyType", back_populates="properties", lazy="joined")
    type_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("property_type.id", ondelete='RESTRICT'),
        nullable=False
    )
    name = sa.Column(sa.String, nullable=False)
    author_name = sa.Column(sa.String, nullable=True)
    description = sa.Column(sa.String, nullable=False)
    added_by = relationship("MerchantDashboard", back_populates="properties", lazy="noload")
    added_by_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('merchant_dashboard.id', ondelete='RESTRICT')
    )
    website = sa.Column(sa.String, nullable=True)
    phone = sa.Column(sa.String, nullable=False)

    address = sa.Column(sa.String, nullable=False)
    latitude = sa.Column(sa.Float, nullable=False)
    longitude = sa.Column(sa.Float, nullable=False)
    city = relationship("City", back_populates="properties", lazy="joined")
    city_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('city.id', ondelete='RESTRICT')
    )

    is_breakfast_served = sa.Column(sa.Boolean, default=False, nullable=False)
    is_breakfast_included_in_price = sa.Column(sa.Boolean, default=False, nullable=False)

    airport_distance = sa.Column(sa.Float, )
    city_centre_distance = sa.Column(sa.Float, nullable=False)
    railway_distance = sa.Column(sa.Float, )

    star_rating = sa.Column(ENUM(PropertyStarRating), nullable=False)
    total_number_of_rooms = sa.Column(sa.Integer, nullable=False, default=1)

    minimum_price_per_night = sa.Column(sa.Float(precision=10, decimal_return_scale=2), default=0)
    minimum_price_per_night_for_resident = sa.Column(sa.Float(precision=10, decimal_return_scale=2), default=0)

    checkin_from = sa.Column(sa.DateTime(timezone=True))
    checkin_until = sa.Column(sa.DateTime(timezone=True))
    checkout_from = sa.Column(sa.DateTime(timezone=True))
    checkout_until = sa.Column(sa.DateTime(timezone=True))

    is_active = sa.Column(ENUM(PropertyStatus), default=PropertyStatus.PENDING, nullable=False)

    pets_allowed = sa.Column(sa.Boolean, default=False, nullable=False)
    smoking_allowed = sa.Column(sa.Boolean, default=False, nullable=False)

    translations = relationship("PropertyTranslation", backref="property", lazy="selectin")
    rooms = relationship("PropertyRoomTemplate", back_populates="property", lazy="selectin")
    photos = relationship("PropertyPhoto", back_populates="property", lazy="selectin")
    services = relationship("PropertyService", back_populates="property", lazy="selectin")
    bookings = relationship("Booking", lazy="noload")
    languages = relationship("PropertyLanguage", back_populates="property", lazy="selectin")
    review_questions = relationship("PropertyReviewQuestion", back_populates="property", lazy="noload")
    rating = relationship("PropertyRating", back_populates="property", uselist=False, lazy="selectin")

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()


class PropertyLanguage(Base):
    property_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('property.id', ondelete='CASCADE'),
        nullable=False
    )
    language_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('language.id', ondelete='CASCADE'),
        nullable=False
    )
    property = relationship("Property", back_populates="languages", lazy="noload")
    language = relationship("Language", lazy="joined")

    def __repr__(self):
        return 'Property lang Id {}'.format(self.id)

    def __str__(self):
        return 'Property lang Id {}'.format(self.id)


class PropertyPhoto(Base):
    photo_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("doc_file.id"))
    photo = relationship("DocFile", lazy='selectin')
    property_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('property.id', ondelete='CASCADE')
    )
    property = relationship("Property", back_populates="photos")
    is_default = sa.Column(sa.Boolean, default=False)

    def __repr__(self):
        return 'Photo Id {}'.format(self.id)

    def __str__(self):
        return 'Photo Id {}'.format(self.id)


class PropertyService(Base):
    property_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('property.id', ondelete='CASCADE')
    )
    property = relationship("Property", lazy="noload")
    icon_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("doc_file.id"))
    icon = relationship("DocFile", lazy="selectin")
    service_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("service.id", ondelete='RESTRICT')
    )
    service = relationship("Service", lazy="selectin")

    def __repr__(self):
        return 'PropertyService Id {}'.format(self.id)

    def __str__(self):
        return 'PropertyService Id {}'.format(self.id)


class UserFavourite(Base):
    user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id', ondelete='CASCADE'))
    user = relationship("User", lazy="noload")
    property_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('property.id', ondelete='CASCADE')
    )
    property = relationship("Property", lazy="noload")

    def __repr__(self):
        return 'UserFavourite Id {}'.format(self.id)

    def __str__(self):
        return 'UserFavourite Id {}'.format(self.id)


class PropertyTypeTranslation(TranslationBase):
    property_type_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("property_type.id", ondelete='CASCADE'),
        nullable=False
    )
    type = sa.Column(sa.String, nullable=False)

    def __repr__(self):
        return 'PropertyTypeTranslation Id {}'.format(self.id)

    def __str__(self):
        return 'PropertyTypeTranslation Id {}'.format(self.id)


class PropertyTranslation(TranslationBase):
    property_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('property.id', ondelete='CASCADE'),
        nullable=False
    )
    description = sa.Column(sa.String, nullable=False)
    address = sa.Column(sa.String, nullable=False)

    def __repr__(self):
        return 'PropertyTranslation Id {}'.format(self.id)

    def __str__(self):
        return 'PropertyTranslation Id {}'.format(self.id)


# === EVENT LISTENERS === #

@event.listens_for(Property, "after_insert")
def receive_after_property_insert(mapper, connection, target):
    app_logger.info(str(mapper))
    # TODO: check property's dashboard, make the property default if default_property is None
