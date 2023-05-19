from faker import Faker

from app.models import MerchantTopicTranslation, MerchantTopic
from app.models.enums import Languages
from ._conf import ModelData

fake = Faker()
fake_ru = Faker(locale="ru_RU")
fake_uz = Faker(locale='tr_TR')

DATAS = [
    {
        "title": fake.text(),
        "description": fake.text(),
        "translations": ModelData(
            MerchantTopicTranslation,
            [
                {
                    "language": Languages.RU,
                    "title": fake_ru.text(),
                    "description": fake_ru.text()
                },
                {
                    "language": Languages.UZ,
                    "title": fake_uz.text(),
                    "description": fake_uz.text()
                },
            ],
            parent_field_name='topic_id'
        )
    }
    for _ in range(10)
]
model_data = ModelData(
    MerchantTopic,
    data=DATAS,
    check_records=True
)
