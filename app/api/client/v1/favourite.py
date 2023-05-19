from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app import schemas
from app.api import deps
from app.crud import crud_favourite
from app.models import User

router = APIRouter()


# Todo: Add pagination
@router.get('/me/', response_model=schemas.UserFavouriteProperties)
async def me(
        current_user: User = Depends(deps.get_current_user)
):
    favourite_list = await crud_favourite.favourite_list(current_user.id)
    return dict(user=current_user, properties=favourite_list)


@router.post('/create/', response_model=List[int])
async def create_or_delete_favourite(
        user_favourite: schemas.UserFavourite,
        user: User = Depends(deps.get_current_user),
):
    favourite_ = await crud_favourite.create_or_delete_favourite(user_id=user.id,
                                                                 property_id=user_favourite.property_id)
    if favourite_ is True:
        return JSONResponse({
            'ok': True,
            'detail': "User favourite deleted"
        })
    elif favourite_ is None:
        return JSONResponse({
            'ok': False,
            'detail': "Can't add more than 20 hotels to favorites"
        }, status_code=405)
    return JSONResponse({
        'ok': True,
        'detail': "User favourite created",
    }, status_code=201)
