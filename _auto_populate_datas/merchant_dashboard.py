from app.models.user import MerchantDashboard
from ._conf import ModelData

model_data = ModelData(
    MerchantDashboard,
    data=[
        {
            'balance': 1_000_000,
            'chief_id': 1,
            'default_property_id': 1,
        }
    ]
)
