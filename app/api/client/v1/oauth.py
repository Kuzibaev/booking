from fastapi import APIRouter, Depends, Request
from fastapi.routing import APIRoute
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.api import deps
from app.core.security import Auth
from app.crud import oauth_base, crud_user, facebook_oauth
from app.crud.google import google_oauth
from app.schemas.oauth import (
    OAuthRedirectLink,
    OAuthUserDataResponseSchema,
    OAuthCodeResponseSchema
)

router = APIRouter()


@router.get("/google/login/", response_model=OAuthRedirectLink, name='google_login_url')
@router.get("/facebook/login/", response_model=OAuthRedirectLink, name='facebook_login_url')
async def google_oauth_login_request(request: Request) -> OAuthRedirectLink:
    route: APIRoute = request.scope['route']
    if route.name == 'google_login_url':
        return google_oauth.generate_link_for_code()
    return facebook_oauth.generate_link_for_code()


@router.post("/google/verify/", response_model=OAuthUserDataResponseSchema, name='google_verify')
@router.post("/facebook/verify/", response_model=OAuthUserDataResponseSchema, name='facebook_verify')
async def oauth_webhook(request: Request, data: OAuthCodeResponseSchema):
    try:
        route: APIRoute = request.scope['route']
        if route.name == 'google_verify':
            token = await google_oauth.get_token(data.code)
            social_acc_data = await google_oauth.get_user_data(token)
        else:
            token = await facebook_oauth.get_token(data.code)
            social_acc_data = await facebook_oauth.get_user_data(token)
        social_acc, created = await crud_user.get_or_create_social_acc(social_acc_data)
        return JSONResponse({
            'ok': True,
            'new_user': created,
            'access_token': Auth.create_access_token(social_acc.user_id),
            'refresh_token': Auth.create_refresh_token(social_acc.user_id)
        }, status_code=201 if created else 200)
    except oauth_base.BadRequest as e:
        return JSONResponse(content=e.as_dict(), status_code=400)
