from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import JSONResponse

from app import schemas
from app.api import deps
from app.crud import crud_review
from app.utils.paginator import Paginator, paginate

router = APIRouter()


@router.get('/list/', response_model=schemas.DataResponse[schemas.PropertyReview], status_code=200)
async def get_reviews(
        user: schemas.MerchantUser = Depends(deps.get_current_user),
        paginator: Paginator = Depends(paginate),
):
    if not user.dashboard or not user.dashboard.default_property_id:
        return JSONResponse({'ok': False, 'detail': 'Must choose the main hotel'}, status_code=406)
    return await paginator.execute(
        crud_review.get_reviews_by_property_id(property_id=user.dashboard.default_property_id))


@router.get('/get/qrcode/', status_code=status.HTTP_200_OK)
async def get_qr_code(
        user: schemas.MerchantUser = Depends(deps.get_current_user)):
    if not user.dashboard or not user.dashboard.default_property_id:
        return JSONResponse({'ok': False, 'detail': 'Must choose the main hotel'}, status_code=406)
    return await crud_review.create_qr_code(user.dashboard.default_property_id)
