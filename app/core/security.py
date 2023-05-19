from datetime import datetime, timedelta
from typing import Any, Union, Literal
from uuid import uuid4

from fastapi import HTTPException
from jose import jwt  # noqa: installed with different name. that's why it always complains.
from passlib.context import CryptContext
from pydantic import BaseModel

from .conf import settings


class TokenPayload(BaseModel):
    exp: datetime
    jti: str
    sub: int | str = None
    type: Literal['access', 'refresh']
    user_type: int = 0


class Auth:
    hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")
    algorithm = 'HS256'

    @classmethod
    def _create_token(cls, subject: str | Any, type_token: str, expires_delta: timedelta = None, user_type: int = 0):
        """
        Args:
            user_type (int): this param is used to differentiate users,
                             value can be 1 or 0. 0 - ClientUser, 1 - MerchantUser
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=(
                    settings.ACCESS_TOKEN_EXPIRE_MINUTES if
                    type_token == 'access' else
                    settings.REFRESH_TOKEN_EXPIRE_MINUTES
                )
            )
        to_encode = {
            "exp": expire,
            "sub": str(subject),
            "type": type_token,
            "user_type": str(user_type),
            "jti": str(uuid4())
        }
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=cls.algorithm)

    @classmethod
    def create_access_token(cls, subject: Union[str, Any], expires_delta: timedelta = None, user_type: int = 0) -> str:
        return cls._create_token(
            subject,
            'access',
            expires_delta,
            user_type=user_type,
        )

    @classmethod
    def create_refresh_token(cls, subject: Union[str, Any], expires_delta: timedelta = None, user_type: int = 0) -> str:
        return cls._create_token(
            subject,
            'refresh',
            expires_delta,
            user_type=user_type,
        )

    @classmethod
    def decode_token(cls, token: str, user_type: int = 0) -> TokenPayload:
        try:
            payload = TokenPayload(**jwt.decode(token, settings.SECRET_KEY, algorithms=cls.algorithm))
            if payload.type == 'access' and payload.user_type == user_type:
                return payload
            raise HTTPException(
                status_code=401,
                detail='Invalid scope for token'
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Token expired",
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=401,
                detail='Could not validate credentials'
            )

    @classmethod
    def refresh_token(cls, refresh_token: str, user_type: int = 0):
        try:
            payload = TokenPayload(**jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=cls.algorithm))
            if payload.type == 'refresh' and payload.user_type == user_type:
                new_token = cls.create_access_token(payload.sub, user_type=user_type)
                return new_token
            raise HTTPException(
                status_code=401,
                detail='Invalid scope for token'
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail='Refresh token expired'
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=401,
                detail='Invalid refresh token'
            )

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls.hasher.verify(plain_password, hashed_password)

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return cls.hasher.hash(password)
