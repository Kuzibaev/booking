"""empty message

Revision ID: 66adb64be4f3
Revises: 51b53400d6a9
Create Date: 2023-04-28 11:49:36.428370

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '66adb64be4f3'
down_revision = '51b53400d6a9'
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
    op.add_column('review_question_answer', sa.Column('is_confirmed', sa.Boolean(), nullable=True))
    op.alter_column('transaction', 'balance',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, decimal_return_scale=2),
               existing_nullable=False)
    op.alter_column('transaction', 'amount',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, decimal_return_scale=2),
               existing_nullable=True)
    op.add_column('user_comment', sa.Column('is_confirmed', sa.Boolean(), nullable=True))
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
    op.drop_column('user_comment', 'is_confirmed')
    op.alter_column('transaction', 'amount',
               existing_type=sa.Float(precision=10, decimal_return_scale=2),
               type_=sa.REAL(),
               existing_nullable=True)
    op.alter_column('transaction', 'balance',
               existing_type=sa.Float(precision=10, decimal_return_scale=2),
               type_=sa.REAL(),
               existing_nullable=False)
    op.drop_column('review_question_answer', 'is_confirmed')
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
