from datetime import datetime

import pytz
from fastapi import APIRouter, Depends, Body, status, Security
from fastapi.security import HTTPAuthorizationCredentials
from starlette.responses import JSONResponse

from app import schemas
from app.api import deps
from app.core.conf import settings, eskiz
from app.core.dependencies import get_db
from app.core.security import Auth
from app.crud import crud_merchant_user, crud_user
from app.models import MerchantUser, enums
from app.utils import CodeConfirmation
from app.utils.jwt_token import JWTToken
from app.utils.rate_limiter import rate_limit

router = APIRouter()


@router.put('/update/', response_model=schemas.MerchantUser)
async def update_user_profile(data: schemas.MerchantUserUpdate,
                              current_user: MerchantUser = Depends(deps.get_current_user)):
    if data.new_password:
        if not current_user.check_password(data.old_password):
            return JSONResponse({
                'ok': False,
                'detail': 'Old password is incorrect'
            }, status_code=400)

    return await crud_merchant_user.update(
        db_obj=current_user,
        obj_in=data
    )


@router.post('/update/phone/', response_model=schemas.LoginTokenResponse)
@rate_limit(key=lambda data: data.phone, rate='10/h')
async def update_user_phone(data: schemas.Login,
                            user: MerchantUser = Depends(deps.get_current_user)):
    if user.phone == data.phone:
        return JSONResponse({'ok': False}, status_code=400)
    token, code = await CodeConfirmation.get_code(data.phone)
    if not settings.DEBUG and data.phone != settings.DEBUG_PHONE:
        sms_response = await eskiz.send_sms(data.phone, message=code)
        return {'ok': True, 'token': token, 'message': sms_response.message}
    return {'ok': True, 'token': token}


@router.put("/update/phone/confirm/", response_model=schemas.User)
async def update_user_phone_confirm(token: str = Body(), code: str = Body(),
                                    current_user: MerchantUser = Depends(deps.get_current_user)):
    db = get_db()
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


@router.get('/me/', response_model=schemas.MerchantUser)
async def me(current_user: MerchantUser = Depends(deps.get_current_user)):
    return current_user


@router.get("/logout/", dependencies=[Depends(deps.get_current_user)])
async def logout(auth: HTTPAuthorizationCredentials = Security(deps.auth_scheme)):
    token_blacklisted = await JWTToken.is_blacklisted(auth.credentials)
    token = Auth.decode_token(auth.credentials, user_type=1)
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


@router.get('/forgot/password/')
async def forgot_password(phone: str):
    user: MerchantUser = await crud_user.get_merchant_by_phone(phone)
    if user.is_active and user is not None:
        if user.role == enums.MerchantUserRole.CHIEF and user.dashboard:
            token, code = await CodeConfirmation.get_code(user.phone)
            if not settings.DEBUG and user.phone != settings.DEBUG_PHONE:
                sms_response = await eskiz.send_sms(user.phone, message=code)
                return {'ok': True, 'token': token, 'message': sms_response.message}
            return {'ok': True, 'token': token}
        else:
            JSONResponse({
                'ok': True,
                'detail': "You are not allowed to do so."
            })
    elif not user.is_active:
        return JSONResponse({
            'ok': True,
            'detail': 'User is not active'
        })
    return JSONResponse({
        'ok': False,
        'detail': 'Bad Request'
    })


@router.post('/reset/password/')
async def reset_password(obj_in: schemas.MerchantUserResetPassword):
    phone = await CodeConfirmation.check_code(obj_in.token, obj_in.code)
    if phone is False:
        return JSONResponse({'ok': False, 'detail': 'Code is invalid'}, status_code=status.HTTP_400_BAD_REQUEST)
    elif phone is None:
        return JSONResponse({'ok': False, 'detail': 'Code is expired'}, status_code=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            if obj_in.new_password == obj_in.new_password2:
                user = await MerchantUser.get_by_phone(phone)
                user.password = obj_in.new_password
                await user.save(refresh=True)
                return JSONResponse({'ok': True, 'detail': 'Successfully Updated'}, status_code=status.HTTP_200_OK)
        except ValueError:
            raise ValueError('Passwords do not match')
    return JSONResponse({'ok': False, 'detail': 'Bad Request'}, status_code=status.HTTP_400_BAD_REQUEST)
