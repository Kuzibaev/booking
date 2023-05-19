from sqladmin import ModelView

from app import models


class ArticleAdmin(ModelView, model=models.Article):
    form_excluded_columns = [
        'id',
        'translations',
        'created_at',
        'updated_at'
    ]
    column_list = ["id", "name", "city", "created_at", "updated_at"]


class ArticleTranslation(ModelView, model=models.ArticleTranslation):
    column_list = ["id", "name", "language", ]
