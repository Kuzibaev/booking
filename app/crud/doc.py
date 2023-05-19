from uuid import UUID

import sqlalchemy as sa

from app import models
from app.schemas import docs as schemas
from .base import CRUDBase
from ..core.dependencies import get_db


class CRUDDocFile(CRUDBase[models.DocFile, schemas.DocFileCreate, schemas.DocFileCreate]):

    async def get(self, *, file_id: UUID):
        db = get_db()
        stmt = sa.select(self.model).where(self.model.id == file_id)
        result = await db.execute(stmt)

        return result.scalar()


crud_doc = CRUDDocFile(models.DocFile)
