import sqlalchemy as sa
from sqlalchemy.sql import operators

from app import models, schemas
from app.models import AboutUs
from .base import CRUDBase
from ..core.dependencies import get_db


class CRUDAbout(CRUDBase):

    @staticmethod
    async def get_about() -> schemas.AboutUs:
        db = get_db()
        stmt = sa.select(models.AboutUs).order_by(operators.desc_op(models.AboutUs.id))
        result = (await db.execute(stmt)).scalars().first()
        return result


about = CRUDAbout(model=AboutUs)
