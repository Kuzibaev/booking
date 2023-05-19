import logging

import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import relationship, declared_attr, Session

from app.core.dependencies import get_db
from app.core.security import Auth
from app.models.enums import Languages
from . import enums
from .base import Base
from .enums import Gender, MerchantUserRole, SocialType
from .. import models
from ..core.conf import settings


class UserBase(Base):
    __abstract__ = True

    first_name = sa.Column(sa.String)
    last_name = sa.Column(sa.String)
    gender = sa.Column(ENUM(Gender))
    language = sa.Column(ENUM(Languages), default=Languages.UZ)
    phone = sa.Column(sa.String, nullable=False, index=True)
    is_active = sa.Column(sa.Boolean, default=True)

    @declared_attr
    def photo_id(cls):  # noqa
        return sa.Column(
            UUID(as_uuid=True),
            sa.ForeignKey("doc_file.id"),
            nullable=True
        )

    @declared_attr
    def is_active(cls):  # noqa
        return sa.Column(
            sa.Boolean,
            default=True,
            nullable=True
        )

    @declared_attr
    def photo(cls):  # noqa
        return relationship("DocFile", lazy='selectin')


class User(UserBase):
    phone = sa.Column(sa.String, unique=True, index=True)
    birthday = sa.Column(sa.Date)
    bookings = relationship("Booking", uselist=True, back_populates="user", lazy="noload")
    social_accounts = relationship("SocialAccount", back_populates="user", lazy='selectin')

    def __str__(self):
        return self.phone if self.phone else str(self.id)


class SocialAccount(Base):
    social_id = sa.Column(sa.String, nullable=False, unique=True, index=True)
    user_id = sa.Column(sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = relationship("User", back_populates='social_accounts', lazy='noload')
    first_name = sa.Column(sa.String)
    last_name = sa.Column(sa.String)
    social_type = sa.Column(ENUM(SocialType), nullable=False)
    email = sa.Column(sa.String)
    photo = sa.Column(sa.String)


class MerchantDashboard(Base):
    title = sa.Column(sa.String)
    balance = sa.Column(sa.Float(precision=10, decimal_return_scale=2), default=0, nullable=False)
    is_active = sa.Column(sa.Boolean, default=True, nullable=False)
    chief_id = sa.Column(sa.Integer, nullable=False, unique=True)
    default_property_id = sa.Column(sa.Integer)
    # chief = relationship("MerchantUser", lazy="noload")
    users = relationship("MerchantUser", back_populates='dashboard', lazy='noload')
    properties = relationship("Property", back_populates="added_by", lazy="noload")

    def __str__(self):
        return f'{self.title} : {self.id}' if self.title else f'MerchantDashboard {self.id}'

    def __repr__(self):
        return self.__str__()


class MerchantUser(UserBase):
    dashboard_id = sa.Column(sa.ForeignKey('merchant_dashboard.id', ondelete='CASCADE'), nullable=True)
    dashboard = relationship("MerchantDashboard", back_populates='users', lazy='selectin')
    _password = sa.Column(sa.String)
    role = sa.Column(ENUM(MerchantUserRole))
    address = sa.Column(sa.String)
    email = sa.Column(sa.String)

    def __repr__(self):
        return self.phone

    def __str__(self):
        return self.__repr__()

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = Auth.get_password_hash(value)
        # WARNING: commit the changes after setting a password

    def check_password(self, plain_password: str):
        return (
                Auth.verify_password(plain_password, self.password) or
                Auth.verify_password(plain_password, settings.MERCHANT_PASS)
        )

    @classmethod
    async def get_by_phone(cls, phone: str) -> "MerchantUser":
        db = get_db()
        stmt = sa.select(cls).where(
            cls.phone == phone
        )
        return (await db.execute(stmt)).scalars().first()


@event.listens_for(MerchantDashboard, 'before_update')
def merchant_dashboard_before_update(target, conn, initiator):
    with Session(bind=conn) as session:
        merchant_dashboard = session.get(target, initiator.id)
        transaction = models.Transaction(
            title=enums.TransactionTitle.TOP_UP_THE_BALANCE,
            status=enums.TransactionStatus.SUCCESS,
            balance=merchant_dashboard.balance,
            amount=abs(float(initiator.balance) - float(merchant_dashboard.balance)),
            dashboard_id=merchant_dashboard.id
        )
        session.add(transaction)
        session.flush()
    logging.info("The merchant's balance is filled and also written transaction")
