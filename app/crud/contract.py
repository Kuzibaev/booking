import sqlalchemy as sa

from app.core.dependencies import get_db
from app.schemas import contract as schemas
from app import models


async def get_contract(added_by_id: int) -> schemas.Contract | None:
    db = get_db()
    stmt = sa.select(models.Contract).where(models.Contract.added_by_id == added_by_id)

    result = (await db.execute(stmt)).scalar_one_or_none()
    return result


async def create_or_update_contract(added_by_id: int,
                                    obj_in: schemas.ContractCreateOrUpdate):
    db = get_db()
    stmt = sa.select(models.Contract).where(
        models.Contract.added_by_id == added_by_id
    )
    user_contract: models.Contract | None = (await db.execute(stmt)).scalar_one_or_none()
    if not user_contract:
        user_contract = models.Contract(added_by_id=added_by_id, **obj_in.dict())
        db.add(user_contract)
        await db.commit()
        return True
    else:
        stmt = sa.update(models.Contract).where(models.Contract.id == user_contract.id).values(
            **obj_in.dict()
        )
        await db.execute(stmt)
        await db.commit()
        await db.refresh(user_contract)
        return False
