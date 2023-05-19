from datetime import datetime

import pytz
from fastapi import APIRouter, Depends, Body, status, Security
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.api import deps
from app.core.dependencies import get_db
from app.core.conf import settings, eskiz
from app.core.security import Auth
from app.crud import crud_user
from app.models import User
from app.utils import CodeConfirmation
from app.utils.jwt_token import JWTToken
from app.utils.rate_limiter import rate_limit

router = APIRouter(dependencies=[Depends(deps.get_current_user)])


@router.put('/update/', response_model=schemas.User)
async def update_user_profile(data: schemas.UserUpdate,
                              current_user: User = Depends(deps.get_current_user),
                              ):
    user_ = await crud_user.update(
        db_obj=current_user,
        obj_in=data
    )
    return user_


@router.post('/update/phone/', response_model=schemas.LoginTokenResponse)
@rate_limit(key=lambda data: data.phone, rate='10/h')
async def update_user_phone(data: schemas.Login, user: User = Depends(deps.get_current_user)):
    if user.phone == data.phone:
        return JSONResponse({'ok': False}, status_code=400)
    token, code = await CodeConfirmation.get_code(data.phone)
    if not settings.DEBUG and data.phone != settings.DEBUG_PHONE:
        sms_response = await eskiz.send_sms(data.phone, message=code)
        return {'ok': True, 'token': token, 'message': sms_response.message}
    return {'ok': True, 'token': token}


@router.put("/update/phone/confirm/", response_model=schemas.User)
async def update_user_phone_confirm(token: str = Body(), code: str = Body(),
                                    current_user: User = Depends(deps.get_current_user),
                                    db: AsyncSession = Depends(deps.get_db)):
    phone = await CodeConfirmation.check_code(token, code)
    if phone is False:
        return JSONResponse({'ok': False, 'detail': 'Code is invalid'}, status_code=status.HTTP_400_BAD_REQUEST)
    elif phone is None:
        return JSONResponse({'ok': False, 'detail': 'Code is expired'}, status_code=status.HTTP_400_BAD_REQUEST)
    else:
        current_user.phone = phone
        await db.commit()
        await db.refresh(current_user)
        return current_user


@router.get('/me/', response_model=schemas.User)
async def me(current_user: User = Depends(deps.get_current_user)):
    return current_user


@router.get("/logout/", dependencies=[Depends(deps.get_current_user)])
async def logout(auth: HTTPAuthorizationCredentials = Security(deps.auth_scheme)):
    token_blacklisted = await JWTToken.is_blacklisted(auth.credentials)
    token = Auth.decode_token(auth.credentials)
    if token_blacklisted:
        return JSONResponse({
            'ok': False,
            'detail': 'Token has already blacklisted'
        }, status_code=400)
    await JWTToken.blacklist_token(auth.credentials, ex=int((token.exp - datetime.now(tz=pytz.UTC)).total_seconds()))
    return JSONResponse({
        'ok': True,
        'detail': 'Token is blacklisted'
    })


@router.delete('/delete/')
async def delete_user(user: User = Depends(deps.get_current_user)):
    db = get_db()
    if user:
        user.is_active = False
        db.add(user)
        await db.commit()
        return JSONResponse({'ok': True, 'detail': 'Successfully deleted'}, status_code=200)
    return JSONResponse({'ok': False, 'detail': 'Not Found'}, status_code=404)
