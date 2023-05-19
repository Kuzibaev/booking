import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from .base import CRUDBase


class CRUDFaq(CRUDBase):
    @staticmethod
    async def get_all_faq(db: AsyncSession, page: int = 1, per_page: int = 50):
        skip = per_page * (page - 1)
        query = sa.select(
            models.Faq
        )

        query = query.offset(skip).limit(per_page)

        result = (await db.execute(query)).scalars().all()
        return result

    async def create_faq(self, db: AsyncSession, faq: schemas.FaqCreate):
        instance = models.Faq(**faq.dict(exclude={'translations'}))
        db.add(instance)
        await db.commit()
        await db.refresh(instance)
        for tr in faq.translations:
            db.add(models.FaqTranslation(faq_id=instance.id, **tr.dict()))
        if faq.translations:
            await db.commit()


crud_faq = CRUDFaq(model=models.Faq)
