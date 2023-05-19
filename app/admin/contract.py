from sqladmin import ModelView

from app import models


class ContractAdmin(ModelView, model=models.Contract):
    column_list = [
        'id',
        'added_by',
        'contract_date',
        'contract_number',
        'firma_type',
        'city',
        'address',
        'zip_code',
        'phone',
        'phone',
        'payment_account',
        'usd_block',
        'oked',
        'bank',
        'mfo',
        'inn',
        'okonh',
        'based',
        'author'
    ]
    can_edit = False
    can_delete = False
