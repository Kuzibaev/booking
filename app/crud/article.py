import sqlalchemy as sa
from sqlalchemy import desc
from sqlalchemy.sql import operators

from app import models, schemas
from .base import CRUDBase
from ..core.dependencies import get_db


class CRUDArticle(CRUDBase):

    @staticmethod
    def get_articles(cities: list[int] = None):
        query = sa.select(
            models.Article
        ).order_by(desc(models.Article.created_at))
        if cities:
            query = query.where(
                operators.in_op(models.Article.city_id, cities)
            )
        return query

    @staticmethod
    async def create_article(obj_in: schemas.ArticleCreate) -> models.Article:
        db = get_db()
        article_instance = models.Article(**obj_in.dict(exclude_none=True, exclude={'translations'}))
        db.add(article_instance)
        await db.commit()
        await db.refresh(article_instance)
        for translation in obj_in.translations:
            db.add(models.ArticleTranslation(article_id=article_instance.id, **translation.dict(exclude_none=True)))

        await db.commit()
        await db.refresh(article_instance)
        return article_instance


crud_article = CRUDArticle(model=models.Article)

# Article
