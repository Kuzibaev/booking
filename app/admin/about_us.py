from sqladmin import ModelView

from app import models


class AboutUsAdmin(ModelView, model=models.AboutUs):
    name = "About us"
    name_plural = name
    column_list = ["id", "phone", "text", "email"]
    form_excluded_columns = [
        'id',
        'translations',
        'created_at',
        'updated_at'
    ]


class AboutUsTranslation(ModelView, model=models.AboutUsTranslation):
    name = "About us translation"
    name_plural = "About us translations"
    column_list = ['id', 'text', 'language']


class Faq(ModelView, model=models.Faq):
    form_excluded_columns = [
        'id',
        'translations',
        'created_at',
        'updated_at'
    ]
    column_list = ["id", "question", "answer"]


class FaqTranslation(ModelView, model=models.FaqTranslation):
    column_list = ["id", "question", "language"]
