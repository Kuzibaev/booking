from app.models import AboutUs, AboutUsTranslation
from app.models.enums import Languages
from ._conf import ModelData

DATAS = [
    {
        "text": """What is Lorem Ipsum?
                    Lorem Ipsum is simply dummy text of the printing and typesetting industry. 
                    Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book.
                    It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of
                    Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum""",
        "phone": "+998901234567",
        "email": "info@email.com",
        "address": "Tashkent",
        "latitude": 44.25590,
        "longitude": 69.2948504,
        "telegram_username": "example_username",
        "translations": ModelData(
            AboutUsTranslation,
            [
                {
                    "language": Languages.RU,
                    "text": """What is Lorem Ipsum?
                    Lorem Ipsum is simply dummy text of the printing and typesetting industry. 
                    Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book.
                    It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of
                    Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum""",
                    "address": "Tashkent",
                },
                {
                    "language": Languages.UZ,
                    "text": """What is Lorem Ipsum?
                    Lorem Ipsum is simply dummy text of the printing and typesetting industry. 
                    Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book.
                    It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of
                    Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum""",
                    "address": "Tashkent",
                },
            ],
            parent_field_name='about_us_id'
        )
    }
]
model_data = ModelData(
    AboutUs,
    data=DATAS,
    check_records=True
)
