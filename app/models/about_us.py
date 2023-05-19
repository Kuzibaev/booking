import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .base import Base, TranslationBase


class AboutUs(Base):
    text = sa.Column(sa.Text, nullable=False)
    phone = sa.Column(sa.String)
    email = sa.Column(sa.String)
    address = sa.Column(sa.String)
    latitude = sa.Column(sa.Float)
    longitude = sa.Column(sa.Float)
    telegram_username = sa.Column(sa.String)
    translations = relationship("AboutUsTranslation", back_populates='about_us', lazy='selectin')


# Translation tables
class AboutUsTranslation(TranslationBase):
    text = sa.Column(sa.String, nullable=False)
    address = sa.Column(sa.String)
    about_us_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("about_us.id", ondelete='CASCADE'),
        nullable=False
    )
    about_us = relationship("AboutUs", back_populates='translations', lazy='noload')


class Faq(Base):
    question = sa.Column(sa.String, nullable=False)
    answer = sa.Column(sa.String, nullable=False)
    translations = relationship("FaqTranslation", back_populates='faq', lazy='selectin')


# Translation tables
class FaqTranslation(TranslationBase):
    question = sa.Column(sa.String, nullable=False)
    answer = sa.Column(sa.String, nullable=False)
    faq_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('faq.id', ondelete='CASCADE'),
        nullable=False
    )
    faq = relationship("Faq", back_populates='translations', lazy='noload')
