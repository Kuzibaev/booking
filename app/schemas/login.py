from pydantic import BaseModel

from .base import PhoneNumber


class Login(BaseModel):
    phone: PhoneNumber


class LoginTokenResponse(BaseModel):
    ok: bool
    token: str
    message: str = None
