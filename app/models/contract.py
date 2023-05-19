import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .base import Base


class Contract(Base):
    added_by = relationship("MerchantDashboard", lazy="noload", uselist=False)
    added_by_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('merchant_dashboard.id'),
        nullable=False,
        unique=True
    )
    contract_date = sa.Column(sa.Date)
    contract_number = sa.Column(sa.String)
    firma_type = sa.Column(sa.String)
    city = sa.Column(sa.String)
    address = sa.Column(sa.String)
    zip_code = sa.Column(sa.String)
    phone = sa.Column(sa.String)
    payment_account = sa.Column(sa.String)
    usd_block = sa.Column(sa.Float(precision=10, decimal_return_scale=2), default=0.0)
    oked = sa.Column(sa.String)
    bank = sa.Column(sa.String)
    mfo = sa.Column(sa.String)
    inn = sa.Column(sa.String)
    okonh = sa.Column(sa.String, nullable=True)
    based = sa.Column(sa.String, nullable=False)
    author = sa.Column(sa.String, nullable=False)

    def __str__(self):
        return self.contract_number

    def __repr__(self):
        return self.__str__()
