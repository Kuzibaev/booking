from faker import Faker

from app.models import FaqTranslation, Faq
from app.models.enums import Languages
from ._conf import ModelData

fake = Faker()
fake_ru = Faker(locale="ru_RU")
fake_uz = Faker(locale='tr_TR')
DATAS = [
    {
        "question": fake.text(),
        "answer": fake.sentence(),
        'translations': ModelData(
            FaqTranslation,
            [
                {
                    'language': Languages.UZ,
                    'question': fake_uz.text(),
                    'answer': fake_uz.sentence(),
                },
                {
                    'language': Languages.EN,
                    'question': fake.text(),
                    'answer': fake.sentence(),
                },
                {
                    'language': Languages.RU,
                    'question': fake_ru.text(),
                    'answer': fake_ru.sentence(),
                },
            ], 'faq_id'
        )
    } for _ in range(10)
]

model_data = ModelData(
    Faq,
    data=DATAS,
    check_records=True
)
