from typing import Optional, Union

import sqlalchemy as sa

from app import models
from app.core.dependencies import get_db


class CRUDUserFavourite:
    @staticmethod
    async def get_favourite(user_id: int, property_id: int) -> Optional[models.UserFavourite]:
        db = get_db()
        query = sa.select(models.UserFavourite).where(
            models.UserFavourite.user_id == user_id, models.UserFavourite.property_id == property_id
        )
        return (await db.execute(query)).scalar_one_or_none()

    async def create_or_delete_favourite(self, *, property_id: int, user_id: int
                                         ) -> Union[bool, models.UserFavourite] | None:
        db = get_db()
        if user_favourite := await self.get_favourite(user_id, property_id):
            await db.delete(user_favourite)
            await db.commit()
            return True
        fav_list = await crud_favourite.favourite_list(user_id)
        if len(fav_list) < 20:
            favourite_instance = models.UserFavourite(user_id=user_id, property_id=property_id)
            db.add(favourite_instance)
            await db.commit()
            await db.refresh(favourite_instance)
            return favourite_instance
        return None

    @staticmethod
    async def favourite_list(user_id: int):
        db = get_db()
        query = sa.select(
            models.Property
        ).select_from(
            models.UserFavourite
        ).join(
            models.Property
        ).where(
            models.UserFavourite.user_id == user_id
        )
        return (await db.execute(query)).scalars().unique().all()


crud_favourite = CRUDUserFavourite()
