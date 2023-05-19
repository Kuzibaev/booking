from typing import Optional

from fastapi import APIRouter, Depends, Body
from starlette import status
from starlette.responses import JSONResponse

from app import schemas, models
from app.api import deps
from app.crud import crud_booking
from app.crud.booking import make_booking_response
from app.utils.paginator import Paginator, paginate

router = APIRouter()


@router.post("/", response_model=schemas.Booking, status_code=201)
async def create_booking(booking_in: schemas.BookingCreate, user: models.User = Depends(deps.get_current_user)):
    if booking := await crud_booking.create(
            user_id=user.id,
            booking_in=booking_in,
    ):
        return make_booking_response(booking)
    return JSONResponse({'ok': False, 'detail': 'Bad Request'}, status_code=400)


@router.get('/all/', response_model=schemas.DataResponse[schemas.Booking])
async def get_all_bookings(
        user: models.User = Depends(deps.get_current_user),
        paginator: Paginator = Depends(paginate)
):
    return await paginator.execute(crud_booking.get_all_bookings(user.id))


@router.get('/history/', response_model=schemas.DataResponse[schemas.BookingHistory], status_code=200)
async def get_all_bookings(
        user: models.User = Depends(deps.get_current_user),
        paginator: Paginator = Depends(paginate)
):
    return await paginator.execute(crud_booking.get_booking_history(user_id=user.id))


@router.get("/{booking_id}/", response_model=schemas.Booking)
async def get_booking(
        booking_id: int,
        user: models.User = Depends(deps.get_current_user)
):
    if booking := await crud_booking.get_booking(booking_id=booking_id, user_id=user.id):
        return make_booking_response(booking)
    elif not booking:
        return JSONResponse({'ok': False, 'detail': 'Not found'}, status_code=status.HTTP_404_NOT_FOUND)
    return JSONResponse({'ok': False, 'detail': 'Internal server error'},
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.put("/{booking_id}/update/", response_model=Optional[schemas.Booking])
async def update_booking(
        booking_id: int,
        booking_in: schemas.BookingUpdate,
        user: models.User = Depends(deps.get_current_user)
):
    if booking := await crud_booking.update_booking(
            booking_in=booking_in,
            booking_id=booking_id,
            user_id=user.id
    ):
        return make_booking_response(booking)
    return JSONResponse({'ok': False, 'detail': 'Not Found'}, status_code=status.HTTP_404_NOT_FOUND)


@router.delete("/{booking_id}/delete/")
async def delete_booking(booking_id: int, reason_of_cancellation: str = Body(None),
                         user: models.User = Depends(deps.get_current_user)):
    is_deleted = await crud_booking.delete_booking(
        booking_id=booking_id,
        user_id=user.id,
        reason_of_cancellation=reason_of_cancellation
    )
    if is_deleted:
        return JSONResponse({'ok': True, 'detail': 'Successfully deleted.'}, status_code=status.HTTP_200_OK)
    return JSONResponse({'ok': False, 'detail': 'Not found'}, status_code=status.HTTP_404_NOT_FOUND)
