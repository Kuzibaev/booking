from sqladmin import ModelView

from app import models


class ServiceCategory(ModelView, model=models.ServiceCategory):
    form_columns = [
        'category_name',
        'is_property_service_category'
    ]

    column_list = [
        'id',
        'category_name',
        'is_property_service_category',
    ]


class ServiceCategoryTranslation(ModelView, model=models.ServiceCategoryTranslation):
    form_columns = [
        'category',
        'language',
        'is_default',
        'category_name'
    ]

    column_list = [
        'id',
        'category',
        'language',
        'is_default',
        'category_name',
    ]


class Service(ModelView, model=models.Service):
    form_columns = [
        'category',
        'service_name',
    ]

    column_list = [
        'id',
        'category',
        'service_name',
    ]


class ServiceTranslation(ModelView, model=models.ServiceTranslation):
    form_columns = [
        'service',
        'language',
        'is_default',
        'service_name',
    ]

    column_list = [
        'id',
        'service',
        'language',
        'is_default',
        'service_name',
    ]
