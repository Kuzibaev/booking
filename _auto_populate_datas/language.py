from app.models import Language, LanguageTranslation
from app.models.enums import Languages
from ._conf import ModelData

model_data = ModelData(
    Language,
    [
        {
            'lang_name': 'Uzbek',
            "translations": ModelData(
                LanguageTranslation,
                [
                    {
                        'language': Languages.UZ,
                        'lang_name': "O'zbek tili"
                    },
                    {
                        'language': Languages.RU,
                        'lang_name': "Узбекский язык"
                    },
                ],
                parent_field_name="language_id"
            )
        },
        {
            'lang_name': 'English',
            "translations": ModelData(
                LanguageTranslation,
                [
                    {
                        'language': Languages.UZ,
                        'lang_name': "Ingliz tili"
                    },
                    {
                        'language': Languages.RU,
                        'lang_name': "Английский"
                    },
                ],
                parent_field_name="language_id"
            )
        },
        {
            'lang_name': 'Russian',
            "translations": ModelData(
                LanguageTranslation,
                [
                    {
                        'language': Languages.UZ,
                        'lang_name': "Rus tili"
                    },
                    {
                        'language': Languages.RU,
                        'lang_name': "Русский"
                    },
                ],
                parent_field_name="language_id"
            )
        },
    ],
    check_records=True
)
