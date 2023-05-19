from typing import Optional

from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import JSONResponse

from app import schemas
from app.api import deps
from app.crud import crud_contract

router = APIRouter()


@router.get('/get/', response_model=Optional[schemas.Contract])
async def get_contract(user: schemas.MerchantUser = Depends(deps.is_chief)):
    if not user.dashboard or not user.dashboard.default_property_id:
        return JSONResponse({'ok': False, 'detail': 'Must choose the main hotel'}, status_code=406)
    result = await crud_contract.get_contract(added_by_id=user.dashboard.id)
    if result:
        return result
    return JSONResponse({'ok': False, 'detail': 'Not Found'}, status_code=status.HTTP_404_NOT_FOUND)


@router.post('/contract/create/', response_model=Optional[schemas.Contract])
async def create_or_update_contact(obj_in: schemas.ContractCreateOrUpdate,
                                   user: schemas.MerchantUser = Depends(deps.is_chief)):
    if not user.dashboard or not user.dashboard.default_property_id:
        return JSONResponse({'ok': False, 'detail': 'Must choose the main hotel'}, status_code=406)
    result = await crud_contract.create_or_update_contract(added_by_id=user.dashboard.id, obj_in=obj_in)
    if result:
        return JSONResponse({'ok': True, 'detail': 'Successfully Created'}, status_code=status.HTTP_201_CREATED)
    return JSONResponse({'ok': True, 'detail': 'Successfully Updated'}, status_code=status.HTTP_200_OK)
