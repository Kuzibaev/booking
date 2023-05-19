from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.enums import SocialType


class OAuthRedirectLink(BaseModel):
    url: str


class OAuthCodeResponseSchema(BaseModel):
    code: str


class OAuthTokenResponseSchema(BaseModel):
    access_token: str
    id_token: str
    expires_in: int
    token_type: str
    scope: Optional[str]
    refresh_token: Optional[str]


class OAuthUserDataResponseSchema(BaseModel):
    """Common interface for integration with external services via OAuth."""

    social_id: str
    email: EmailStr
    social_type: SocialType
    photo: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]

    class Config:
        orm_mode = True
