from sqladmin import ModelView

from app import models


class MerchantDashboard(ModelView, model=models.MerchantDashboard):
    form_columns = [
        "is_active",
        "title",
        "balance",
        "chief_id"
    ]
    column_list = [
        "id",
        "title",
        "is_active",
        "balance",
        "chief_id",
    ]


class MerchantUser(ModelView, model=models.MerchantUser):
    form_columns = [
        "is_active",
        "dashboard",
    ]
    column_list = [
        "id",
        "dashboard",
        "phone",
        "role",
        "address",
        "email",
    ]
