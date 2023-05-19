import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TranslationBase


class City(Base):
    name = sa.Column(sa.String, nullable=False)
    name_slug = sa.Column(sa.String)
    latitude = sa.Column(sa.Float, nullable=False)
    longitude = sa.Column(sa.Float, nullable=False)
    photo_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("doc_file.id"))
    photo = relationship("DocFile", lazy='selectin')

    properties = relationship("Property", back_populates="city", lazy="noload")
    articles = relationship("Article", back_populates="city", lazy="noload")
    translations = relationship("CityTranslation", back_populates="city", lazy="selectin")

    def __repr__(self):
        return f"City id={self.id} slug={self.name_slug}"

    def __str__(self):
        return self.name


class CityTranslation(TranslationBase):
    city_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("city.id", ondelete="CASCADE"),
        nullable=False
    )
    city = relationship("City", back_populates="translations", lazy="noload")
    name = sa.Column(sa.String, nullable=False)

    def __repr__(self):
        return f"{self.name}({self.language})"
