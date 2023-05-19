import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .base import Base, TranslationBase


class Language(Base):
    lang_name = sa.Column(sa.String, nullable=False)
    translations = relationship("LanguageTranslation", back_populates="lang", lazy='selectin')


class LanguageTranslation(TranslationBase):
    lang_name = sa.Column(sa.String, nullable=False)
    language_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("language.id", ondelete="CASCADE"),
        nullable=False
    )
    lang = relationship("Language", back_populates="translations")
