from sqladmin import ModelView

from app import models


class File(ModelView, model=models.DocFile):
    can_create = False
    can_edit = False
    column_list = [
        'id',
        'name',
        'type',
        'path',
    ]
