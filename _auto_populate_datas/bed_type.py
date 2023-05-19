from app import models
from ._conf import ModelData

DATAS = [

    {
        "type": "Single bed"
    },
    {
        "type": "Double bed"
    },
    {
        "type": "Twin beds"
    },
    {
        "type": "Three single beds"
    },
    {
        "type": "Four single beds"
    },
    {
        "type": "Five single beds"
    },
    {
        "type": "Bunk bed"
    },
    {
        "type": "Trestle-bed/Topchan"
    },
    {
        "type": "Seat"
    },
    {
        "type": "Crib"
    },

]

model_data = ModelData(
    models.BedType,
    data=DATAS,
    check_records=True
)

# Single bed
# Twin beds
# Double bed
# Three single beds
# Four single beds
# Five single beds
# Bunk bed
# Trestle-bed/Topchan
# Seat
# Crib
