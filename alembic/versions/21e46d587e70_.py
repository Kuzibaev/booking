"""empty message

Revision ID: 21e46d587e70
Revises: 66adb64be4f3
Create Date: 2023-04-28 22:54:33.816406

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '21e46d587e70'
down_revision = '66adb64be4f3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('booked_room', 'price',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, decimal_return_scale=2),
               existing_nullable=False)
    op.alter_column('booking', 'total_price',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, decimal_return_scale=2),
               existing_nullable=False)
    op.alter_column('contract', 'usd_block',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, decimal_return_scale=2),
               existing_nullable=True)
    op.alter_column('merchant_dashboard', 'balance',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, decimal_return_scale=2),
               existing_nullable=False)
    op.alter_column('property', 'minimum_price_per_night',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, decimal_return_scale=2),
               existing_nullable=True)
    op.alter_column('property', 'minimum_price_per_night_for_resident',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, decimal_return_scale=2),
               existing_nullable=True)
    op.alter_column('property_room_template', 'price',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, decimal_return_scale=2),
               existing_nullable=False)
    op.alter_column('property_room_template', 'price_for_resident',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, decimal_return_scale=2),
               existing_nullable=False)
    op.alter_column('transaction', 'balance',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, decimal_return_scale=2),
               existing_nullable=False)
    op.alter_column('transaction', 'amount',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, decimal_return_scale=2),
               existing_nullable=True)
    op.alter_column('user_comment', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('withdrawal_amount', 'amount',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, decimal_return_scale=2),
               existing_nullable=False)
    op.alter_column('withdrawal_amount', 'amount_for_resident',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, decimal_return_scale=2),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('withdrawal_amount', 'amount_for_resident',
               existing_type=sa.Float(precision=10, decimal_return_scale=2),
               type_=sa.REAL(),
               existing_nullable=False)
    op.alter_column('withdrawal_amount', 'amount',
               existing_type=sa.Float(precision=10, decimal_return_scale=2),
               type_=sa.REAL(),
               existing_nullable=False)
    op.alter_column('user_comment', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('transaction', 'amount',
               existing_type=sa.Float(precision=10, decimal_return_scale=2),
               type_=sa.REAL(),
               existing_nullable=True)
    op.alter_column('transaction', 'balance',
               existing_type=sa.Float(precision=10, decimal_return_scale=2),
               type_=sa.REAL(),
               existing_nullable=False)
    op.alter_column('property_room_template', 'price_for_resident',
               existing_type=sa.Float(precision=10, decimal_return_scale=2),
               type_=sa.REAL(),
               existing_nullable=False)
    op.alter_column('property_room_template', 'price',
               existing_type=sa.Float(precision=10, decimal_return_scale=2),
               type_=sa.REAL(),
               existing_nullable=False)
    op.alter_column('property', 'minimum_price_per_night_for_resident',
               existing_type=sa.Float(precision=10, decimal_return_scale=2),
               type_=sa.REAL(),
               existing_nullable=True)
    op.alter_column('property', 'minimum_price_per_night',
               existing_type=sa.Float(precision=10, decimal_return_scale=2),
               type_=sa.REAL(),
               existing_nullable=True)
    op.alter_column('merchant_dashboard', 'balance',
               existing_type=sa.Float(precision=10, decimal_return_scale=2),
               type_=sa.REAL(),
               existing_nullable=False)
    op.alter_column('contract', 'usd_block',
               existing_type=sa.Float(precision=10, decimal_return_scale=2),
               type_=sa.REAL(),
               existing_nullable=True)
    op.alter_column('booking', 'total_price',
               existing_type=sa.Float(precision=10, decimal_return_scale=2),
               type_=sa.REAL(),
               existing_nullable=False)
    op.alter_column('booked_room', 'price',
               existing_type=sa.Float(precision=10, decimal_return_scale=2),
               type_=sa.REAL(),
               existing_nullable=False)
    # ### end Alembic commands ###
