from faker import Faker

from app.models import DocFile, ArticleTranslation, Article
from app.models.enums import Languages
from ._conf import ModelData, DBRecord

fake = Faker()
fake_ru = Faker(locale="ru_RU")
fake_uz = Faker(locale='tr_TR')

DATAS = [
    {
        "name": fake.text(),
        "description": fake.text(),
        "content": fake.sentence(),
        "photo_id": DBRecord(DocFile, filters=[DocFile.name == 'article_demo_image.jpg']),
        "translations": ModelData(
            ArticleTranslation,
            [
                {
                    "language": Languages.RU,
                    "name": fake_ru.text(),
                    "description": fake_ru.text(),
                    "content": fake_ru.sentence()
                },
                {
                    "language": Languages.UZ,
                    "name": fake_uz.text(),
                    "description": fake_uz.text(),
                    "content": fake_uz.sentence()
                },
            ],
            parent_field_name='article_id'
        )
    }
    for _ in range(10)
]
model_data = ModelData(
    Article,
    data=DATAS,
    check_records=True
)
