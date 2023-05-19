from app.models import PropertyReviewQuestion, PropertyReviewQuestionTranslation
from app.models.enums import Languages
from ._conf import ModelData

model_data = ModelData(
    PropertyReviewQuestion,
    [
        {
            'short_text': 'Cleanliness',
            'text': 'Cleanliness',
            "translations": ModelData(
                PropertyReviewQuestionTranslation,
                [
                    {
                        'language': Languages.UZ,
                        'short_text': 'Tozalik',
                        'text': 'Tozalik',
                    },
                    {
                        'language': Languages.RU,
                        'short_text': 'Чистота',
                        'text': 'Чистота',
                    },
                ],
                parent_field_name="question_id"
            )

        },
        {
            'short_text': 'Dealing culture',
            'text': 'Dealing culture',
            "translations": ModelData(
                PropertyReviewQuestionTranslation,
                [
                    {
                        'language': Languages.UZ,
                        'short_text': 'Davolash madaniyati',
                        'text': 'Davolash madaniyati',
                    },
                    {
                        'language': Languages.RU,
                        'short_text': 'Культура дилинга',
                        'text': 'Культура дилинга',
                    },
                ],
                parent_field_name="question_id"
            )

        },
        {
            'short_text': 'Wifi',
            'text': 'Wifi',
            "translations": ModelData(
                PropertyReviewQuestionTranslation,
                [
                    {
                        'language': Languages.UZ,
                        'short_text': 'Wifi',
                        'text': 'Wifi',
                    },
                    {
                        'language': Languages.RU,
                        'short_text': 'Wifi',
                        'text': 'Wifi',
                    },
                ],
                parent_field_name="question_id"
            )

        },
        {
            'short_text': 'Price and quality',
            'text': 'Price and quality',
            "translations": ModelData(
                PropertyReviewQuestionTranslation,
                [
                    {
                        'language': Languages.UZ,
                        'short_text': 'Narx va sifat',
                        'text': 'Narx va sifat',
                    },
                    {
                        'language': Languages.RU,
                        'short_text': 'Цена и качество',
                        'text': 'Цена и качество',
                    },
                ],
                parent_field_name="question_id"
            )

        }

    ],
    check_records=True
)
