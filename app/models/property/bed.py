import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.models.base import Base, TranslationBase


class BedType(Base):
    type = sa.Column(sa.String, nullable=False)
    translations = relationship("BedTypeTranslation", back_populates="bed_type", lazy="selectin")

    def __str__(self):
        return self.type

    def __repr__(self):
        return self.__str__()


class BedTypeTranslation(TranslationBase):
    bed_type_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('bed_type.id', ondelete='CASCADE'),
        nullable=False
    )
    bed_type = relationship("BedType", back_populates="translations", lazy="noload")
    type = sa.Column(sa.String, nullable=False)
