import logging
from contextlib import suppress
from typing import AsyncIterator

from fastapi import Depends, HTTPException, Security, Request, FastAPI
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from starlette import status

from app import models
from app.core.security import Auth
from app.core.sessions import AsyncSessionLocal
from app.crud import crud_user, crud_merchant_user
from app.models import enums
from app.utils.jwt_token import JWTToken

auth_scheme = HTTPBearer()

logger = logging.getLogger(__name__)


async def get_db() -> AsyncIterator[sessionmaker]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        except HTTPException as http_ex:
            await session.rollback()
            raise http_ex
        finally:
            await session.close()


async def get_current_user(
        request: Request,
        auth: HTTPAuthorizationCredentials = Security(auth_scheme)
):
    app: FastAPI = request.scope['app']
    user_type = 0
    with suppress(AttributeError):
        if app.state.is_merchant:
            user_type = 1
    payload = Auth.decode_token(auth.credentials, user_type)
    if await JWTToken.is_blacklisted(auth.credentials):
        raise HTTPException(
            status_code=401,
            detail='Token is blocked'
        )
    if user_type == 0:
        user = await crud_user.get(id=payload.sub)
    else:
        user = await crud_merchant_user.get_user(user_id=payload.sub)
    if not user:
        raise HTTPException(status_code=403, detail="Forbidden")
    return user


async def is_chief(current_user: models.MerchantUser = Depends(get_current_user)):
    if current_user.role == enums.MerchantUserRole.CHIEF:
        return current_user
    raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Method Not Allowed")
