from sqladmin import ModelView

from app import models


class User(ModelView, model=models.User):
    form_columns = [
        "first_name",
        "last_name",
        "phone",
        "gender",
        "birthday",
        "language",
        "is_active",
    ]
    column_list = [
        models.User.id,
        *form_columns
    ]
