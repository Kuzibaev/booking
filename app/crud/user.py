import sqlalchemy as sa

from app.models.user import User, MerchantUser, SocialAccount
from app.schemas.oauth import OAuthUserDataResponseSchema
from app.schemas.user import UserCreate, UserUpdate
from .base import CRUDBase
from .. import models
from ..core.dependencies import get_db


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_phone(self, phone: str) -> User | None:
        db = get_db()
        query = sa.select(self.model).where(self.model.phone == phone)
        return (await db.execute(query)).scalar_one_or_none()

    async def get(self, id: int) -> User | None:
        db = get_db()
        query = sa.select(self.model).where(self.model.id == id, self.model.is_active == True)
        return (await db.execute(query)).scalar_one_or_none()

    @staticmethod
    async def get_merchant_by_phone(phone: str) -> MerchantUser | None:
        db = get_db()
        query = sa.select(models.MerchantUser).where(models.MerchantUser.phone == phone)
        return (await db.execute(query)).scalar_one_or_none()

    async def get_or_create_social_acc(self, user: OAuthUserDataResponseSchema):
        db = get_db()
        stmt = sa.select(SocialAccount).where(SocialAccount.social_id == user.social_id)
        social_acc = (await db.execute(stmt)).scalar_one_or_none()
        created = False
        if not social_acc:
            user_instance = self.model(first_name=user.first_name)
            db.add(user_instance)
            await db.commit()
            await db.refresh(user_instance)
            social_acc = SocialAccount(
                user_id=user_instance.id,
                **user.dict()
            )
            db.add(social_acc)
            await db.commit()
            await db.refresh(social_acc)
            created = True
        return social_acc, created


crud_user = CRUDUser(model=User)
