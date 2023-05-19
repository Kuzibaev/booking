import re
from typing import NoReturn, Optional, Tuple, List, Any, TypeVar, Type, Dict

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select, operators

from app.core.dependencies import get_db
from app.core.logging import app_logger
from app.core.sessions import AsyncSessionLocal
from app.utils.datetime import utcnow
from app.utils.exceptions import DatabaseValidationError
from .enums import Languages

snake_case_pattern = re.compile(r'(?<!^)(?=[A-Z])')
BaseClass = declarative_base(metadata=sa.MetaData())
TBase = TypeVar("TBase", bound="Base")


class SQLASelect(Select):

    async def __call__(self):
        db: AsyncSessionLocal = get_db()
        return await db.execute(self)

    def __await__(self):
        return self.__call__().__await__()


def select(*args, **kwargs):
    return SQLASelect._create(*args, **kwargs)  # noqa


class Base(BaseClass):
    __abstract__ = True

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = sa.Column(sa.DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:  # noqa
        return snake_case_pattern.sub('_', cls.__name__).lower()

    def __str__(self):
        return f"<{type(self).__name__}({self.id=})>"

    @classmethod
    def _raise_validation_exception(cls, e: IntegrityError) -> NoReturn:
        info = e.orig.args[0] if e.orig.args else ""
        if (match := re.findall(r"Key \((.*)\)=\(.*\) already exists|$", info)) and match[0]:
            raise DatabaseValidationError(f"Unique constraint violated for {cls.__name__}", match[0]) from e
        if (match := re.findall(r"Key \((.*)\)=\(.*\) conflicts with existing key|$", info)) and match[0]:
            field_name = match[0].split(",", 1)[0]
            raise DatabaseValidationError(f"Range overlapped for {cls.__name__}", field_name) from e
        if (match := re.findall(r"Key \((.*)\)=\(.*\) is not present in table|$", info)) and match[0]:
            raise DatabaseValidationError(f"Foreign key constraint violated for {cls.__name__}", match[0]) from e
        app_logger.error("Integrity error for %s: %s", cls.__name__, e)
        raise e

    @classmethod
    def _get_query(cls, prefetch: Optional[Tuple[str, ...]] = None, options: Optional[List[Any]] = None) -> Any:
        query = sa.select(cls)
        if prefetch:
            if not options:
                options = []
            options.extend(selectinload(getattr(cls, x)) for x in prefetch)
            query = query.options(*options).execution_options(populate_existing=True)
        return query

    @classmethod
    async def all(cls: Type[TBase], prefetch: Optional[Tuple[str, ...]] = None) -> List[TBase]:
        query = cls._get_query(prefetch)
        db = get_db()
        db_execute = await db.execute(query)
        return db_execute.scalars().all()

    @classmethod
    async def get_by_id(cls: Type[TBase], obj_id: int, prefetch: Optional[Tuple[str, ...]] = None) -> Optional[TBase]:
        query = cls._get_query(prefetch).where(cls.id == obj_id)
        db = get_db()
        db_execute = await db.execute(query)
        instance = db_execute.scalars().first()
        return instance

    @classmethod
    async def filter(
            cls: Type[TBase],
            filters: Dict[str, Any],
            sorting: Optional[Dict[str, str]] = None,
            prefetch: Optional[Tuple[str, ...]] = None,
    ) -> List[TBase]:
        query = cls._get_query(prefetch)
        db = get_db()
        if sorting is not None:
            query = query.order_by(*cls._build_sorting(sorting))
        db_execute = await db.execute(query.where(sa.and_(True, *cls._build_filters(filters))))
        return db_execute.scalars().all()

    @classmethod
    async def get(
            cls: Type[TBase],
            filters: Dict[str, Any],
            sorting: Optional[Dict[str, str]] = None,
            prefetch: Optional[Tuple[str, ...]] = None,
    ) -> TBase:
        query = cls._get_query(prefetch)
        db = get_db()
        if sorting is not None:
            query = query.order_by(*cls._build_sorting(sorting))
        db_execute = await db.execute(query.where(sa.and_(True, *cls._build_filters(filters))))
        return db_execute.scalars().first()

    @classmethod
    def _build_sorting(cls, sorting: Dict[str, str]) -> List[Any]:
        """Build list of ORDER_BY clauses"""
        result = []
        for field_name, direction in sorting.items():
            field = getattr(cls, field_name)
            result.append(getattr(field, direction)())
        return result

    @classmethod
    def _build_filters(cls, filters: Dict[str, Any]) -> List[Any]:
        """Build list of WHERE conditions"""
        result = []
        for expression, value in filters.items():
            parts = expression.split("__")
            op_name = parts[1] if len(parts) > 1 else "exact"
            if op_name not in operators_map:
                raise KeyError(f"Expression {expression} has incorrect operator {op_name}")
            operator = operators_map[op_name]
            column = getattr(cls, parts[0])
            result.append(operator(column, value))
        return result

    @classmethod
    async def bulk_create(cls: Type[TBase], objects: List[TBase]) -> List[TBase]:
        db: AsyncSessionLocal = get_db()
        try:
            db.add_all(objects)
            await db.flush()
        except IntegrityError as e:
            cls._raise_validation_exception(e)
        return objects

    @classmethod
    async def bulk_update(cls: Type[TBase], objects: List[TBase]) -> List[TBase]:
        db: AsyncSessionLocal = get_db()
        try:
            ids = [x.id for x in objects if x.id]
            await db.execute(sa.select(cls).where(cls.id.in_(ids)))
            for item in objects:
                try:
                    await db.merge(item)
                except IntegrityError as e:
                    cls._raise_validation_exception(e)
            await db.flush()
        except IntegrityError as e:
            cls._raise_validation_exception(e)
        return objects

    async def save(self, commit: bool = True, refresh: bool = False) -> None:
        db: AsyncSessionLocal = get_db()
        db.add(self)
        try:
            if commit:
                await db.commit()
            else:
                await db.flush()
        except IntegrityError as e:
            self._raise_validation_exception(e)
        if refresh:
            await db.refresh(self)

    async def update_attrs(self, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)


class TranslationBase(Base):
    __abstract__ = True

    language = sa.Column(ENUM(Languages), nullable=False)
    is_default = sa.Column(sa.Boolean, default=False, nullable=False)


operators_map = {
    "isnull": lambda c, v: (c is None) if v else (c is not None),
    "exact": operators.eq,
    "ne": operators.ne,  # not equal or is not (for None)
    "gt": operators.gt,  # greater than , >
    "ge": operators.ge,  # greater than or equal, >=
    "lt": operators.lt,  # lower than, <
    "le": operators.le,  # lower than or equal, <=
    "in": operators.in_op,
    "notin": operators.notin_op,
    "between": lambda c, v: c.between(v[0], v[1]),
    "like": operators.like_op,
    "ilike": operators.ilike_op,
    "startswith": operators.startswith_op,
    "istartswith": lambda c, v: c.ilike(v + "%"),
    "endswith": operators.endswith_op,
    "iendswith": lambda c, v: c.ilike("%" + v),
    "overlaps": lambda c, v: getattr(c, "overlaps")(v),
}
