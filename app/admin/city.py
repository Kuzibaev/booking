from sqladmin import ModelView

from app import models


class City(ModelView, model=models.City):
    column_list = ["id", "name_slug", "latitude", "longitude"]
    form_columns = [
        'name',
        'name_slug',
        'latitude',
        'longitude',
    ]


class CityTranslation(ModelView, model=models.CityTranslation):
    column_list = [
        'id',
        'name',
    ]
    form_columns = [
        'city',
        'language',
        'is_default',
        'name',

    ]
