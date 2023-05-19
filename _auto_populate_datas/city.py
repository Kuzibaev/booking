from app.models import City, CityTranslation
from app.models.enums import Languages
from ._conf import ModelData

DATAS = [
    {
        'name': "Tashkent",
        'name_slug': 'tashkent',
        'latitude': 34.3234209384,
        'longitude': 56.34234234,
        'translations': ModelData(
            CityTranslation, [
                {
                    'language': Languages.EN,
                    'name': 'Tashkent'
                },
                {
                    'language': Languages.RU,
                    'name': 'Ташкент'
                },
                {
                    'language': Languages.RU,
                    'name': 'Toshkent'
                }
            ], parent_field_name='city_id'
        )
    },
    {
        'name': "Bukhara",
        'name_slug': 'bukhara',
        'latitude': 34.3234209384,
        'longitude': 56.34234234,
        'translations': ModelData(
            CityTranslation, [
                {
                    'language': Languages.EN,
                    'name': 'Bukhara'
                },
                {
                    'language': Languages.RU,
                    'name': 'Бухара'
                },
                {
                    'language': Languages.UZ,
                    'name': 'Buxoro'
                }
            ], parent_field_name='city_id'
        )
    },
    {
        'name': "Samarkand",
        'name_slug': 'samarkand',
        'latitude': 39.653490891234966,
        'longitude': 66.99878189259454,
        'translations': ModelData(
            CityTranslation, [
                {
                    'language': Languages.EN,
                    'name': 'Samarkand'
                },
                {
                    'language': Languages.RU,
                    'name': 'Самарканд'
                },
                {
                    'language': Languages.UZ,
                    'name': 'Samarqand'
                }
            ], parent_field_name='city_id'
        )
    },
]
model_data = ModelData(
    City, data=DATAS,
    check_records=True
)
