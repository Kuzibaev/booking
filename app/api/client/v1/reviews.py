from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.api import deps
from app.crud import crud_review
from app.utils.paginator import Paginator, paginate

router = APIRouter()


@router.get('/{property_id:int}/question/list/', response_model=list[schemas.ReviewQuestion])
async def get_questions(property_id: int):
    return await crud_review.get_review_questions(property_id)


@router.post('/property/', status_code=201)
async def review_anonymous(obj_in: schemas.ReviewAnonymousAnswerCreate,
                           db: AsyncSession = Depends(deps.get_db)):
    questions = await crud_review.get_review_questions(obj_in.property_id, only_ids=True)
    try:
        obj_in.validate_answers(questions)
        avg = obj_in.get_score_avg(obj_in.answers)
    except ValueError as e:
        return JSONResponse({'ok': False, 'detail': str(e)}, status_code=400)
    await crud_review.create_anonymous_review(db, obj_in, avg)
    return {"ok": True, 'detail': 'Review saved'}


@router.post('/')
async def create_or_update_review(
        booking_id: int,
        obj_in: schemas.ReviewAnswerCreate,
        user: models.User = Depends(deps.get_current_user)):
    questions = await crud_review.get_review_questions(obj_in.property_id, only_ids=True)
    try:
        obj_in.validate_answers(questions)
        avg = obj_in.get_score_avg(obj_in.answers)
    except ValueError as e:
        return JSONResponse({'ok': False, 'detail': str(e)}, status_code=400)
    await crud_review.create_or_update_review(obj_in, user_id=user.id, avg=avg, booking_id=booking_id)
    return {"ok": True, 'detail': 'Review saved'}


@router.get("/{property_id:int}/user/", response_model=schemas.UserReview)
async def get_review(
        property_id: int,
        booking_id: int,
        user: models.User = Depends(deps.get_current_user)
):
    if user_review := await crud_review.get_user_review(
            user_id=user.id,
            property_id=property_id,
            booking_id=booking_id):
        return user_review
    return JSONResponse({"ok": False, 'detail': "Not Found"}, status_code=404)


@router.get('/property/{property_id:int}/reviews/', response_model=list[schemas.PropertyRatingItem])
async def get_property_ratings(property_id: int):
    if property_ratings_items := await crud_review.get_property_ratings(property_id):
        return property_ratings_items
    return JSONResponse({"ok": True, 'detail': "Bad Request"}, status_code=400)


@router.get('/property/{property_id}/comments/',
            response_model=schemas.DataResponse[schemas.UserComment], status_code=200)
async def get_property_comments(
        property_id: int,
        paginator: Paginator = Depends(paginate)):
    return await paginator.execute(crud_review.get_property_comments(property_id))
