from http.client import HTTPException

from eskiz_sms.exceptions import EskizException
from fastapi import APIRouter, Body, status, Request
from fastapi.responses import JSONResponse

from app import schemas
from app.core.conf import settings, eskiz
from app.core.security import Auth
from app.crud import crud_user
from app.utils import CodeConfirmation
from app.utils.rate_limiter import rate_limit

router = APIRouter()


@router.post("/", response_model=schemas.LoginTokenResponse)
@rate_limit(key=lambda login: login.phone, rate='20/h')
async def check_phone(login: schemas.Login = None):
    token, code = await CodeConfirmation.get_code(login.phone)
    if not settings.DEBUG and login.phone != settings.DEBUG_PHONE:
        try:
            resp = await eskiz.send_sms(login.phone, message=settings.ESKIZ_SMS_TEXT.format(code=code))
        except EskizException as e:
            return JSONResponse({'ok': False, 'detail': str(e)})
        else:
            return {'ok': True, 'token': token, 'message': resp.message}
    return {'ok': True, 'token': token}


@router.post('/confirm/')
async def check_code(request: Request, token: str = Body(), code: str = Body()):
    phone = await CodeConfirmation.check_code(token, code)
    if phone:
        user_ = await crud_user.get_by_phone(phone=phone)
        if user_ is None:
            user_ = await crud_user.create(obj_in=schemas.UserCreate(
                phone=phone, language=request.state.language,
            ), use_jsonable_encoder=False)
            new_user, status_code = True, 201
        elif user_.is_active == False:
            return JSONResponse(
                {
                    'ok': False,
                    'detail': 'You cannot log in with this number, this number blocked'
                },
                status_code=403
            )
        else:
            new_user, status_code = False, 200
        return JSONResponse({
            'ok': True,
            'new_user': new_user,
            'access_token': Auth.create_access_token(user_.id),
            'refresh_token': Auth.create_refresh_token(user_.id)
        }, status_code=status_code)
    return JSONResponse({
        'ok': False,
        'detail': ('Code is expired' if phone is None else 'Code is invalid')
    },
        status_code=status.HTTP_400_BAD_REQUEST
    )


@router.post('/token/refresh/')
async def refresh(refresh_token: str):
    try:
        new_access_token = Auth.refresh_token(refresh_token)
        new_refresh_token = Auth.create_refresh_token(new_access_token[0])
        return dict(access_token=new_access_token, refresh_token=new_refresh_token)
    except HTTPException as e:
        return JSONResponse({'detail': str(e)}, status_code=400)
