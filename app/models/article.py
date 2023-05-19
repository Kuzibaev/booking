import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TranslationBase


class Article(Base):
    name = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String, nullable=False)
    content = sa.Column(sa.String, nullable=False)
    photo_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("doc_file.id"))
    photo = relationship("DocFile", lazy='selectin')
    city_id = sa.Column(sa.Integer, sa.ForeignKey("city.id"))
    city = relationship("City", back_populates="articles", lazy="joined")
    translations = relationship("ArticleTranslation", back_populates="article", lazy='selectin')


# Translation tables
class ArticleTranslation(TranslationBase):
    name = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String, nullable=False)
    content = sa.Column(sa.String, nullable=False)
    article_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('article.id', ondelete='CASCADE'),
        nullable=False
    )
    article = relationship("Article", back_populates='translations')
