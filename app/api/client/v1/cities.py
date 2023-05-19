from fastapi import APIRouter, Depends

from app import schemas
from app.crud import crud_city
from app.utils.paginator import Paginator, paginate

router = APIRouter()


@router.get('/list/', response_model=schemas.DataResponse[schemas.City])
async def get_cities(paginator: Paginator = Depends(paginate)):
    return await paginator.execute(crud_city.get_multi())


@router.get('/{slug:str}/', response_model=schemas.City)
async def get_city_by_slug(slug: str):
    return await crud_city.get_by_slug(slug)
