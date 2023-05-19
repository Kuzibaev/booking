from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import JSONResponse

from app import schemas
from app.api import deps
from app.crud import crud_transaction
from app.utils.paginator import Paginator, paginate

router = APIRouter()


@router.get('/', response_model=schemas.DataResponse[schemas.Transaction])
async def get_all_transactions(
        paginator: Paginator = Depends(paginate),
        user: schemas.MerchantUser = Depends(deps.get_current_user)):
    if not user.dashboard or not user.dashboard.default_property_id:
        return JSONResponse({'ok': False, 'detail': 'Must choose the main hotel'}, status_code=406)
    return await paginator.execute(
        crud_transaction.get_all_transactions_by_property_id(property_id=user.dashboard.default_property_id,
                                                             dashboard_id=user.dashboard.id))
