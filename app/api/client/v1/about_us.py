from typing import Optional

from fastapi import APIRouter

from app.crud import crud_about
from app.schemas import AboutUs

router = APIRouter()


@router.get("/", response_model=Optional[AboutUs])
async def get_about():
    return await crud_about.get_about()
