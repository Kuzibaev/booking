from app import models
from sqladmin import ModelView


class WithDraw(ModelView, model=models.WithdrawalAmount):
    form_columns = [
        'room_type_id',
        'room_type',
        'amount',
        'amount_unit',
        'amount_for_resident',
        'amount_unit_for_resident'
    ]

    column_list = [
        'id',
        *form_columns
    ]


class Transactions(ModelView, model=models.Transaction):
    column_list = [
        'id',
        'title',
        'status',
        'order_id',
        'property',
        'balance',
        'amount',
        'room_type',
    ]
    can_create = False
    can_export = True
    can_edit = False
    can_delete = False
