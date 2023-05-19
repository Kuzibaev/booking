import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import operators

from app import models, schemas
from app.core.dependencies import get_db
from app.models.enums import MerchantUserRole


async def get_user(user_id: int, is_chief: bool = False,
                   dashboard_id: int | None = None) -> models.MerchantUser | None:
    db = get_db()
    if is_chief:
        stmt = sa.select(models.MerchantUser).where(
            models.MerchantUser.id == user_id,
            models.MerchantUser.dashboard_id == dashboard_id
        )

        return (await db.execute(stmt)).scalars().first()
    else:
        stmt = sa.select(models.MerchantUser).where(
            models.MerchantUser.id == user_id
        )

        return (await db.execute(stmt)).scalars().first()


def get_personal_users(dashboard_id: int):
    query = sa.select(models.MerchantUser).where(
        models.MerchantUser.dashboard_id == dashboard_id,
        models.MerchantUser.role == MerchantUserRole.MANAGER
    ).order_by(operators.desc_op(models.MerchantUser.created_at))

    return query


async def create(db: AsyncSession, phone: str, first_name: str, last_name: str, password: str):
    instance = models.MerchantUser(
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        role=MerchantUserRole.CHIEF,
        password=password
    )
    db.add(instance)
    await db.commit()
    await db.refresh(instance)
    merchant_dashboard_instance = models.MerchantDashboard(chief_id=instance.id)
    db.add(merchant_dashboard_instance)
    await db.commit()
    instance.dashboard_id = merchant_dashboard_instance.id
    db.add(instance)
    await db.commit()
    await db.refresh(instance)
    return instance


async def update(db_obj: models.MerchantUser, obj_in: schemas.MerchantUserUpdate):
    db = get_db()
    db_obj.first_name = obj_in.first_name or db_obj.first_name
    db_obj.last_name = obj_in.last_name or db_obj.last_name
    db_obj.photo_id = obj_in.photo_id or None
    if obj_in.new_password:
        setattr(db_obj, 'password', obj_in.new_password)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def update_personal_user(user_id: int, obj_in: schemas.PersonalUserUpdate, dashboard_id: int):
    db = get_db()
    personal_user = await get_user(user_id=user_id, dashboard_id=dashboard_id, is_chief=True)
    if personal_user:
        personal_user.first_name = obj_in.first_name
        personal_user.last_name = obj_in.last_name
        personal_user.email = obj_in.email
        personal_user.address = obj_in.address
        personal_user.phone = obj_in.phone

        if obj_in.photo_id:
            personal_user.photo_id = obj_in.photo_id

        if obj_in.new_password:
            setattr(personal_user, 'password', obj_in.new_password)
        await db.commit()
        await db.refresh(personal_user)
        return True
    return False
