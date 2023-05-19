from app.models import SavedFilter, SavedFilterTranslation, PropertyType
from app.models.enums import Languages
from ._conf import ModelData, DBRecord

_p_type = DBRecord(PropertyType)
model_data = ModelData(
    SavedFilter,
    data=[
        {
            "name": 'For family',
            "price_gte": 400_000,
            "price_lte": 1_200_000,
            "property_types": [
                _p_type([PropertyType.type == "Hotel"]),
                _p_type([PropertyType.type == "Otel"]),
            ],
            "city_centre_distances": [5, 6],
            "ratings": [6, 7, 10],
            "star_ratings": [5],
            "translations": ModelData(
                SavedFilterTranslation,
                data=[
                    {
                        'name': 'For family',
                        'language': Languages.EN
                    },
                    {
                        'name': 'Oila uchun',
                        'language': Languages.UZ
                    },
                    {
                        'name': 'Для семьи',
                        'language': Languages.RU
                    },
                ],
                parent_field_name="filter_id"
            ),
        },
        {
            "name": "Business trip",
            "price_gte": 1_000_000,
            "price_lte": 2_500_000,
            "property_types": [
                _p_type([PropertyType.type == "Hotel"]),
                _p_type([PropertyType.type == "Otel"]),
            ],
            "city_centre_distances": [10, 20],
            "ratings": [3, 5],
            "star_ratings": [4, 5],
            "translations": ModelData(
                SavedFilterTranslation,
                data=[
                    {
                        'name': 'Business trip',
                        'language': Languages.EN
                    },
                    {
                        'name': 'Komandirovka',
                        'language': Languages.UZ
                    },
                    {
                        'name': 'Командировка',
                        'language': Languages.RU
                    },
                ],
                parent_field_name="filter_id"
            ),
        },
    ],
    check_records=True
)
