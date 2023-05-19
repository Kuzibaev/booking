import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import operators

from app import models, schemas
from .base import CRUDBase
from ..core.dependencies import get_db


class CRUDCity(CRUDBase):
    @staticmethod
    async def get_cities(
            db: AsyncSession, *, q: str = None, lang: str = None,
            page: int = 1,
            per_page: int = 10,
    ):
        offset = per_page * (page - 1)
        query = sa.select(
            models.City.id,
            sa.literal('city', type_=sa.Unicode).label("type"),
            # models.CityTranslation.name,
            sa.func.coalesce(models.CityTranslation.name, models.City.name).label('name'),
            models.City.name_slug,
            models.City.latitude,
            models.City.longitude,
            sa.func.count(models.Property.id).label('properties')
        ).select_from(models.CityTranslation).outerjoin(
            models.City, models.City.id == models.CityTranslation.city_id
        ).outerjoin(
            models.Property, models.Property.city_id == models.City.id
        ).offset(offset).limit(per_page).group_by(
            models.City.id,
            models.CityTranslation.name
        )
        if q:
            query = query.where(
                operators.ilike_op(
                    models.CityTranslation.name,
                    f"%{q}%"
                )
            )
        elif lang:
            query = query.where(
                models.CityTranslation.language == lang
            )
        else:
            query = query.where(
                operators.is_(models.CityTranslation.is_default, True)
            )
        result = (await db.execute(query)).fetchall()
        return result

    @staticmethod
    async def create_city(db: AsyncSession, *, obj_in: schemas.CityCreate):
        city_instance = models.City(**obj_in.dict(exclude_none=True, exclude={'translations'}))
        db.add(city_instance)
        await db.commit()
        await db.refresh(city_instance)
        for translation in obj_in.translations:
            db.add(models.CityTranslation(city_id=city_instance.id, **translation.dict(exclude_none=True)))
        await db.commit()
        await db.refresh(city_instance)
        return city_instance

    async def get_by_slug(self, slug: str) -> models.City | None:
        db = get_db()
        stmt = sa.select(self.model).where(self.model.name_slug == slug)
        return (await db.execute(stmt)).scalar_one_or_none()


crud_city = CRUDCity(models.City)
