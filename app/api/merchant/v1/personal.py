from typing import Optional

from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import JSONResponse

from app import schemas
from app.api import deps
from app.crud import crud_merchant_user, crud_user
from app.models import MerchantUser, enums
from app.utils.paginator import paginate, Paginator

router = APIRouter()


@router.get('/list/', response_model=schemas.DataResponse[schemas.PersonalUser], status_code=status.HTTP_200_OK)
async def get_users(
        user: schemas.PersonalUser = Depends(deps.is_chief),
        paginator: Paginator = Depends(paginate)
):
    return await paginator.execute(crud_merchant_user.get_personal_users(user.dashboard.id))


@router.get('/get/{user_id}/', response_model=Optional[schemas.PersonalUser], status_code=status.HTTP_200_OK)
async def get_user(user_id: int, user: schemas.PersonalUser = Depends(deps.is_chief)):
    return (await crud_merchant_user.get_user(
        user_id=user_id,
        is_chief=True,
        dashboard_id=user.dashboard.id)
            )


@router.post('/create/', response_model=Optional[schemas.PersonalUser], status_code=status.HTTP_201_CREATED)
async def create_user(user_in: schemas.PersonalUserCreate, user: schemas.MerchantUser = Depends(deps.is_chief)):
    user_ = await crud_user.get_merchant_by_phone(phone=user_in.phone)
    if user_ is None:
        merchant_user = MerchantUser(
            first_name=user_in.first_name,
            last_name=user_in.last_name,
            password=user_in.password,
            phone=user_in.phone,
            address=user_in.address,
            photo_id=user_in.photo_id,
            role=enums.MerchantUserRole.MANAGER,
            dashboard_id=user.dashboard.id,
        )
        await merchant_user.save(refresh=True)

        return merchant_user
    return JSONResponse({'ok': True, 'detail': 'Phone number already exists'}, status_code=400)


@router.put('/update/{user_id}/', response_model=Optional[schemas.PersonalUser], status_code=status.HTTP_200_OK)
async def update_user(user_id: int,
                      user_in: schemas.PersonalUserUpdate,
                      user: schemas.MerchantUser = Depends(deps.is_chief)
                      ):
    user_ = await crud_user.get_merchant_by_phone(user_in.phone)
    if not user_:
        is_update = await crud_merchant_user.update_personal_user(user_id, user_in, dashboard_id=user.dashboard.id)
        if is_update:
            return JSONResponse({'ok': True, 'detail': 'Successfully Updated'}, status_code=status.HTTP_200_OK)
    return JSONResponse({'ok': False, 'detail': 'Phone number already exists'}, status_code=status.HTTP_400_BAD_REQUEST)
