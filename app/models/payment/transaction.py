import sqlalchemy as sa
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.enums import TransactionStatus, TransactionTitle


class Transaction(Base):
    title = sa.Column(sa.Enum(TransactionTitle), nullable=False)
    status = sa.Column(sa.Enum(TransactionStatus), nullable=False)
    order_id = sa.Column(sa.Integer, nullable=True)

    property_id = sa.Column(sa.ForeignKey("property.id"), nullable=True)
    property = relationship("Property", lazy="noload")
    balance = sa.Column(sa.Float(precision=10, decimal_return_scale=2), nullable=False)
    amount = sa.Column(sa.Float(precision=10, decimal_return_scale=2), default=0, nullable=True)

    dashboard_id = sa.Column(sa.ForeignKey("merchant_dashboard.id"), nullable=False)
    dashboard = relationship("MerchantDashboard", lazy="noload")
    room_type_id = sa.Column(sa.ForeignKey("room_type.id"), nullable=True)
    room_type = relationship("RoomType", lazy="selectin")

    def __str__(self):
        return f'{self.title} : {self.status}'

    def __repr__(self):
        return self.__str__()
