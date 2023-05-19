from pydantic import BaseModel

from .property import Property
from .user import User


class UserFavouriteProperties(BaseModel):
    user: User
    properties: list[Property]


class UserFavourite(BaseModel):
    property_id: int
