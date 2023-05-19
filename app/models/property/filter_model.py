import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.models.base import Base, TranslationBase


class SavedFilter(Base):
    name = sa.Column(sa.String, nullable=False, unique=True)
    price_gte = sa.Column(sa.Float, default=0, nullable=False)
    price_lte = sa.Column(sa.Float, default=0, nullable=False)
    property_types = sa.Column(sa.ARRAY(sa.Integer), server_default="{}", nullable=False)
    city_centre_distances = sa.Column(sa.ARRAY(sa.Float), server_default="{}", nullable=False)
    star_ratings = sa.Column(sa.ARRAY(sa.Integer), server_default="{}", nullable=False)
    ratings = sa.Column(sa.ARRAY(sa.Float), server_default="{}", nullable=False)
    other_filters = sa.Column(sa.JSON)
    translations = relationship("SavedFilterTranslation", backref="filter", lazy="selectin")


class SavedFilterTranslation(TranslationBase):
    filter_id = sa.Column(sa.ForeignKey('saved_filter.id', ondelete='CASCADE'), nullable=False)
    name = sa.Column(sa.String, nullable=False)
