import json
from collections.abc import Iterable
from importlib import import_module
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import BinaryExpression

from app.models.base import Base

_CURRENT_DIR = Path(__file__).parent
with open(_CURRENT_DIR / 'hotels.json') as file:
    HOTELS = json.load(file)


class DBRecord:
    def __init__(self, model: type[Base], filters: list[Any] = None, order_by: list[Any] = None):
        self.model = model
        self._filters = filters or []
        self._order_by = order_by or []
        self.__left = None

    async def get(self, session: AsyncSession, field_name: str = "id"):
        record = (await session.execute(self._build_query())).scalar_one_or_none()
        if not record:
            text = ", ".join([f"{f.__str__()}" for f in self._filters])
            raise ValueError((
                f"{self.model.__name__} {text} is not found"
            ))
        return getattr(record, field_name)

    def _build_query(self):
        tables = set()
        stmt = select(self.model)
        _model_cols = (col for col in self.model.__table__.columns)
        for _filter in self._filters:
            if _filter.left not in _model_cols:
                tables.add(_filter.left.table)
        for table in tables:
            stmt = stmt.join(table)
        if self._filters:
            stmt = stmt.where(*self._filters)
        if self._order_by:
            stmt = stmt.order_by(self._order_by)
        return stmt.limit(1)

    def __call__(self, filters: list[Any] = None, order_by: list[Any] = None, merge_filters: bool = True):
        filters = filters or []
        order_by = order_by or []
        if merge_filters:
            filters += self._filters
        return self.__class__(
            model=self.model,
            filters=filters or self._filters,
            order_by=order_by or self._order_by,
        )

    def __eq__(self, other):
        if isinstance(other, BinaryExpression):
            self.__left = other


class ModelData:

    def __init__(
            self, model: type[Base], data: list,
            parent_field_name: str = None, check_records: bool = False
    ):
        self.model = model
        self.data = data
        self.depends_on: set[type[Base]] = set()
        self.parent_field_name = parent_field_name
        self.check_records = check_records

        self._find_depends_on_classes()

    def _find_depends_on_classes(self, data: list = None):
        for data_ in (data or self.data):
            if isinstance(data_, Iterable):
                if isinstance(data_, dict):
                    data_ = data_.values()
                for v_ in data_:
                    if isinstance(v_, list):
                        self._find_depends_on_classes(v_)
                    elif isinstance(v_, dict):
                        self._find_depends_on_classes([v_])
                    elif isinstance(v_, DBRecord):
                        self.depends_on.add(v_.model)
                    elif isinstance(v_, ModelData):
                        self.depends_on.update(v_.depends_on)
            elif isinstance(data_, DBRecord):
                self.depends_on.add(data_.model)

    async def record_exist(self, session: AsyncSession):
        return bool(
            (await session.execute(select(self.model).limit(1))).scalar_one_or_none()
        )

    async def save(self, session: AsyncSession, parent_id: int = None):
        if self.check_records:
            if await self.record_exist(session):
                return
        for _dict in self.data:
            _modified_dict = {}
            if parent_id:
                _modified_dict[self.parent_field_name] = parent_id
            _children = set()
            for _k, _v in _dict.items():
                if isinstance(_v, DBRecord):
                    _modified_dict[_k] = await _v.get(session)
                elif isinstance(_v, ModelData):
                    _children.add(_v)
                else:
                    if isinstance(_v, list):
                        _v_values = []
                        for _v_val in _v:
                            if isinstance(_v_val, DBRecord):
                                _v_values.append(await _v_val.get(session))
                            else:
                                _v_values.append(_v_val)
                        _modified_dict[_k] = _v_values
                    else:
                        _modified_dict[_k] = _v
            _instance = self.model(**_modified_dict)
            session.add(_instance)
            await session.commit()
            await session.refresh(_instance)
            for _child in _children:
                await _child.save(session, _instance.id)

    def __str__(self):
        return f"<{self.model.__name__} deps=[{', '.join([model.__name__ for model in self.depends_on])}]>"

    def __repr__(self):
        return self.__str__()


def find_files():
    files = [
        f.stem
        for f in _CURRENT_DIR.glob('*.py')
        if not f.stem.startswith("_")
    ]
    return files


def _get_model_data(file_name) -> ModelData | None:
    f_path = '.'.join([_CURRENT_DIR.stem, file_name])
    imported_file = import_module(f_path)
    return getattr(imported_file, 'model_data', None)


def _resolve_model_data_order(model_data_list: list[ModelData]) -> list[ModelData]:
    _all_classes, _seen_classes = set(), set()
    for _model_data in model_data_list:
        _all_classes.add(_model_data.model)
    _ordered_model_data_list = []

    while model_data_list:
        m_data = model_data_list.pop(0)
        for dependant in _all_classes.intersection(m_data.depends_on):
            if dependant not in _seen_classes:
                model_data_list.append(m_data)
                break
        else:
            _seen_classes.add(m_data.model)
            _ordered_model_data_list.append(m_data)
    return _ordered_model_data_list


def get_model_datas() -> list[ModelData]:
    model_data_list: list[ModelData] = []
    files = find_files()
    for f in files:
        if model_data := _get_model_data(f):
            model_data_list.append(model_data)
    return _resolve_model_data_order(model_data_list)
