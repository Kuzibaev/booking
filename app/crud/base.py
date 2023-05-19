from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

import sqlalchemy as sa
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.models.base import Base, BaseClass

ModelType = TypeVar("ModelType", bound=BaseClass)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    @staticmethod
    async def __commit(db: AsyncSession):
        try:
            await db.commit()
        except SQLAlchemyError as exp:
            await db.rollback()
            raise exp
        return True

    async def __save(self, db: AsyncSession, instance: "Base"):
        db.add(instance)
        await self.__commit(db)
        await db.refresh(instance)
        return instance

    async def get(self, id: Any) -> Optional[ModelType]:
        db = get_db()
        query = sa.select(self.model).where(self.model.id == id)
        result = (await db.execute(query)).scalars().first()
        return result

    def get_multi(self):
        return sa.select(self.model)

    async def create(self, obj_in: CreateSchemaType, use_jsonable_encoder=True) -> ModelType:
        db = get_db()
        if use_jsonable_encoder:
            obj_in = jsonable_encoder(obj_in)
        else:
            obj_in = obj_in.dict()
        db_obj = self.model(**obj_in)  # type: ignore
        return await self.__save(db, db_obj)

    async def update(
            self,
            *,
            db_obj: ModelType,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        db = get_db()
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        return await self.__save(db, db_obj)

    async def remove(self, db: AsyncSession, *, id: int) -> bool:
        query = sa.delete(self.model).where(self.model.id == id)
        await db.execute(query)
        return await self.__commit(db)
