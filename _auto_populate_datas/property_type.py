from app.models import PropertyTypeTranslation, PropertyType
from app.models.enums import Languages
from ._conf import ModelData

DATAS = [
    {
        'type': 'Hotel',
        'translations': ModelData(
            PropertyTypeTranslation,
            [
                {'language': Languages.UZ, 'type': 'Mehmonxona'},
                {'language': Languages.EN, 'type': 'Hotel'},
                {'language': Languages.RU, 'type': 'Гостиница'},
            ],
            'property_type_id'
        )
    },
    {
        'type': 'Otel',
        'translations': ModelData(
            PropertyTypeTranslation,
            [
                {'language': Languages.UZ, 'type': 'Otel'},
                {'language': Languages.EN, 'type': 'Otel'},
                {'language': Languages.RU, 'type': 'Отель'},
            ],
            'property_type_id'
        )
    },
]

model_data = ModelData(
    PropertyType,
    data=DATAS,
    check_records=True
)
