import sqlalchemy as sa

from app import models


def get_all_transactions_by_property_id(property_id: int, dashboard_id: int):
    query = sa.select(models.Transaction).outerjoin(
        models.Property, models.Transaction.property_id == models.Property.id
    ).outerjoin(
        models.MerchantDashboard, models.Transaction.dashboard_id == models.MerchantDashboard.id
    ).where(
        sa.or_(
            models.Transaction.property_id == property_id,
            sa.and_(
                models.Transaction.property_id == None,
                models.Transaction.dashboard_id == dashboard_id
            )
        ),
    )

    return query.order_by(sa.desc(models.Transaction.created_at))
