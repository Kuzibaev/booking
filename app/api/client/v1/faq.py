from fastapi import APIRouter, Depends

from app import schemas
from app.crud import crud_faq
from app.utils.paginator import Paginator, paginate

router = APIRouter()


@router.get("/", response_model=schemas.DataResponse[schemas.Faq])
async def get_faq(paginator: Paginator = Depends(paginate)):
    return await paginator.execute(crud_faq.get_multi())
