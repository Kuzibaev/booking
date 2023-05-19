from datetime import datetime

from pydantic import BaseModel

from app.models import enums
from .property_room import RoomType


class Transaction(BaseModel):
    id: int
    title: enums.TransactionTitle
    status: enums.TransactionStatus
    order_id: int
    balance: float

    amount: float
    room_type: RoomType
    created_at: datetime

    class Config:
        orm_mode = True
