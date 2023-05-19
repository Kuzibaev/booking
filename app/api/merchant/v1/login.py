from eskiz_sms.exceptions import EskizException
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app import schemas
from app.api import deps
from app.core.conf import settings, eskiz
from app.core.security import Auth
from app.crud import crud_merchant_user, crud_user
from app.utils import CodeConfirmation
from app.utils.rate_limiter import rate_limit

router = APIRouter()


class Login(BaseModel):
    phone: str
    password: str


class Register(BaseModel):
    code: str
    token: str
    first_name: str
    last_name: str
    password: str


@router.post("/")
@rate_limit(key=lambda data: data.phone, rate='20/h')
async def login(data: Login):
    user = await crud_user.get_merchant_by_phone(data.phone)

    if user and user.check_password(data.password):
        return JSONResponse({
            'ok': True,
            'access_token': Auth.create_access_token(user.id, user_type=1),
            'refresh_token': Auth.create_refresh_token(user.id, user_type=1)
        })
    return JSONResponse({
        'ok': False,
        'detail': 'Login or password is invalid'
    }, status_code=401)


@router.post("/check-phone/")
@rate_limit(key=lambda data: data.phone, rate='20/h')
async def check_phone(data: schemas.Login):
    user = await crud_user.get_merchant_by_phone(data.phone)
    if user:
        return JSONResponse({'ok': False, 'detail': 'User with this phone number exists'}, status_code=400)
    token, code = await CodeConfirmation.get_code(data.phone)
    if not settings.DEBUG and data.phone != settings.DEBUG_PHONE:
        try:
            resp = await eskiz.send_sms(data.phone, message=settings.ESKIZ_SMS_TEXT.format(code=code))
        except EskizException as e:
            return JSONResponse({'ok': False, 'detail': str(e)})
        else:
            return {'ok': True, 'token': token, 'message': resp.message}
    return {'ok': True, 'token': token}


@router.post("/register/", response_model=schemas.MerchantUser)
async def register(data: Register, db: AsyncSession = Depends(deps.get_db)):
    phone = await CodeConfirmation.check_code(data.token, data.code)
    if phone is False:
        return JSONResponse({
            'ok': False,
            'detail': 'Code is invalid'
        })
    user = await crud_merchant_user.create(db, phone, data.first_name, data.last_name, data.password)
    return user


@router.post('/token/refresh/')
async def refresh(refresh_token: str):
    try:
        new_access_token = Auth.refresh_token(refresh_token, user_type=1)
        new_refresh_token = Auth.create_refresh_token(new_access_token[0], user_type=1)
        return dict(access_token=new_access_token, refresh_token=new_refresh_token)
    except HTTPException as e:
        return JSONResponse({'detail': str(e)}, status_code=400)
