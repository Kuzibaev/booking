from fastapi import APIRouter, Depends, Query
from starlette.responses import JSONResponse

from app import schemas
from app.crud import crud_article
from app.utils.paginator import Paginator, paginate

router = APIRouter()


@router.get("/list", response_model=schemas.DataResponse[schemas.Article])
async def get_articles(
        cities: list[int] = Query(None, alias='cities'),
        paginator: Paginator = Depends(paginate)
):
    return await paginator.execute(crud_article.get_articles(cities))


@router.get("/{article_id}/", response_model=schemas.Article)
async def get_article_by_id(article_id: int):
    if article_ := await crud_article.get(id=article_id):
        return article_
    return JSONResponse({'ok': False, 'detail': 'Not Found'}, status_code=404)
