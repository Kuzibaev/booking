import sqlalchemy as sa
from fastapi import Query
from sqlalchemy.sql import Select

from app.core.dependencies import get_db


class Paginator:
    def __init__(self):
        self.limit = 10
        self.offset = 0

    def __call__(self, page: int = Query(default=1), per_page: int = Query(10, alias='per-page')):
        self.limit = per_page
        self.offset = per_page * (page - 1)
        return self

    async def execute(self, query: Select, fetch_one: bool = False):
        db = get_db()
        total = (await db.execute(sa.select(sa.func.count()).select_from(query.subquery()))).scalar_one()
        db_execute = await db.execute(query.limit(self.limit).offset(self.offset))
        if fetch_one:
            items = db_execute.scalars().unique().first()
        else:
            items = db_execute.scalars().unique().all()

        return dict(items=items, total=total)


paginate = Paginator()
