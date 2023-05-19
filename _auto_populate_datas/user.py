from faker import Faker

from app import models
from app.models.enums import Languages, Gender
from ._conf import ModelData

fake = Faker()

DATAS = [
    {
        "first_name": fake.first_name_male(),
        "last_name": fake.last_name_male(),
        "phone": "+998901234567",
        "gender": Gender.MALE,
        "language": Languages.EN
    }
]

model_data = ModelData(
    models.User,
    DATAS,
    check_records=True
)
