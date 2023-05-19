from app.models import MerchantUser
from app.models.enums import Gender, Languages, MerchantUserRole
from ._conf import ModelData

model_data = ModelData(
    MerchantUser,
    data=[
        {
            "first_name": "Johnny",
            "last_name": "Depp",
            "phone": "+998901234567",
            "password": 'secret',
            "gender": Gender.MALE,
            "role": MerchantUserRole.CHIEF,
            "language": Languages.EN,
            # "dashboard_id": 1,
        }
    ]
)
