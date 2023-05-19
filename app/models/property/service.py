import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.models.base import Base, TranslationBase


class ServiceCategory(Base):
    category_name = sa.Column(sa.String, nullable=False)
    is_property_service_category = sa.Column(sa.Boolean, default=False)
    services = relationship("Service", back_populates="category", lazy="selectin")
    translations = relationship("ServiceCategoryTranslation", lazy="selectin")

    def __str__(self):
        return '{}'.format(self.category_name)

    def __repr__(self):
        return self.__str__()


class Service(Base):
    category_id = sa.Column(sa.Integer, sa.ForeignKey("service_category.id"))
    service_name = sa.Column(sa.String, nullable=False)
    category = relationship("ServiceCategory", back_populates="services", lazy="selectin")
    translations = relationship("ServiceTranslation", lazy="selectin")

    def __str__(self):
        return '{}'.format(self.service_name)

    def __repr__(self):
        return self.__str__()


class ServiceCategoryTranslation(TranslationBase):
    category = relationship("ServiceCategory", back_populates="translations")
    category_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('service_category.id', ondelete='CASCADE'),
        nullable=False
    )

    category_name = sa.Column(sa.String, nullable=False)

    def __str__(self):
        return '{}'.format(self.category_name)

    def __repr__(self):
        return self.__str__()


class ServiceTranslation(TranslationBase):
    service = relationship("Service", back_populates='translations')
    service_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('service.id', ondelete='CASCADE'),
        nullable=False
    )
    service_name = sa.Column(sa.String, nullable=False)

    def __str__(self):
        return '{}'.format(self.service_name)

    def __repr__(self):
        return self.__str__()
