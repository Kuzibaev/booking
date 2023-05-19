import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.enums import BillingUnit


class WithdrawalAmount(Base):
    room_type_id = sa.Column(sa.ForeignKey('room_type.id', ondelete='CASCADE'), nullable=False)
    room_type = relationship("RoomType", lazy='noload')
    amount = sa.Column(sa.Float(precision=10, decimal_return_scale=2), nullable=False)
    amount_unit = sa.Column(ENUM(BillingUnit), default=BillingUnit.FIXED_VALUE, nullable=False)
    amount_for_resident = sa.Column(sa.Float(precision=10, decimal_return_scale=2), nullable=False)
    amount_unit_for_resident = sa.Column(ENUM(BillingUnit), default=BillingUnit.FIXED_VALUE, nullable=False)
