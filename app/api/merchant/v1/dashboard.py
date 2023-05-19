from datetime import date
from typing import List

from fastapi import APIRouter, Depends, Query, Body
from starlette.responses import JSONResponse

from app import schemas, models
from app.api import deps
from app.core.conf import settings, eskiz
from app.models import enums
from app.crud import crud_booking
from app.models.enums import CountByDays
from app.utils.paginator import Paginator, paginate
from app.utils.sms_message import order_accept_send_sms

router = APIRouter()


@router.get("/")
async def accounting(user: schemas.MerchantUser = Depends(deps.get_current_user),
                     days: CountByDays = CountByDays.LAST_30_DAYS):
    if not user.dashboard or not user.dashboard.default_property_id:
        return JSONResponse({'ok': False, 'detail': 'Must choose the main hotel'}, status_code=406)
    return await crud_booking.get_accounting(property_id=user.dashboard.default_property_id, days=days)


@router.get('/orders/', response_model=schemas.DataResponse[schemas.Booking])
async def get_orders(
        paginator: Paginator = Depends(paginate),
        sort_by: enums.OrderSortBy = Query('by_date', alias='sort_by'),
        user: schemas.MerchantUser = Depends(deps.get_current_user)):
    if not user.dashboard or not user.dashboard.default_property_id:
        return JSONResponse({'ok': False, 'detail': 'Must choose the main hotel'}, status_code=406)
    return await paginator.execute(
        crud_booking.get_orders(property_id=user.dashboard.default_property_id, sort_by=sort_by))


@router.get('/orders-statistics/')
async def get_orders_statistics(user: schemas.MerchantUser = Depends(deps.get_current_user)):
    if not user.dashboard or not user.dashboard.default_property_id:
        return JSONResponse({'ok': False, 'detail': 'Must choose the main hotel'}, status_code=406)
    return await crud_booking.get_orders_statistics(property_id=user.dashboard.default_property_id)


@router.get('/orders/{booking_id}/', response_model=schemas.Booking, dependencies=[Depends(deps.get_current_user)])
async def get_order(booking_id: int):
    if booking := await crud_booking.get_order(booking_id):
        return booking
    return JSONResponse({'ok': False, 'detail': 'Not Found'}, status_code=404)


@router.post('/cancel/order/{booking_id}')
async def cancel_order(
        booking_id: int,
        reason_of_cancellation: str = Body(None),
        is_cancel: bool = Body(False),
        is_arrived: bool = Body(False),
        user: schemas.MerchantUser = Depends(deps.get_current_user)
):
    if not user.dashboard or not user.dashboard.default_property_id:
        return JSONResponse({'ok': False, 'detail': 'Must choose the main hotel'}, status_code=406)
    user, is_canceled = await crud_booking.cancel_order(
        booking_id=booking_id,
        property_id=user.dashboard.default_property_id,
        reason_of_cancellation=reason_of_cancellation,
        is_arrived=is_arrived,
        is_cancel=is_cancel
    )
    if is_canceled:
        user: models.User
        if user.phone:
            text = order_accept_send_sms(user.language, is_accept=False)
            await eskiz.send_sms(user.phone, text)
        return JSONResponse({'ok': False, 'detail': 'Successfully Canceled'},
                            status_code=200)
    return JSONResponse({'ok': False, 'detail': 'Bad Request'}, status_code=400)


@router.post('/accept/order/')
async def accept_or_cancel_order(
        booking_id: int,
        obj_in: List[schemas.AcceptOrderWithRoom],
        accept_or_cancel: enums.AcceptOrCancel,
        user: schemas.MerchantUser = Depends(deps.get_current_user)):
    if not user.dashboard or not user.dashboard.default_property_id:
        return JSONResponse({'ok': False, 'detail': 'Must choose the main hotel'}, status_code=406)

    booking_ = await crud_booking.get_booking_(booking_id=booking_id, property_id=user.dashboard.default_property_id)
    total_with_draw_amount = sum(
        with_draw for with_draw, _ in
        [await crud_booking.with_draw_amount(room) for room in booking_.rooms]
    )

    if user.dashboard.balance < total_with_draw_amount:
        return JSONResponse({'ok': False, 'detail': 'You need to top up your balance to accept the order.'},
                            status_code=422)

    is_accepted, status_code, user = await crud_booking.accept_or_cancel_order(
        property_id=user.dashboard.default_property_id,
        added_by_id=user.dashboard.id,
        booking_id=booking_id,
        obj_in=obj_in,
        accept_or_cancel=accept_or_cancel
    )

    if is_accepted:
        if status_code == 201:
            if not settings.DEBUG and user.phone != settings.DEBUG_PHONE:
                user: models.User
                if user.phone:
                    text = order_accept_send_sms(user.language)
                    response_message = await eskiz.send_sms(user.phone, text)
                    return JSONResponse(
                        {'ok': True, 'detail': 'Successfully Accepted', 'message': f'{response_message.message}'},
                        status_code=201)
            return JSONResponse({'ok': True, 'detail': 'Successfully Accepted'}, status_code=201)
        elif status_code == 402:
            return JSONResponse({'ok': True, 'detail': 'Payment Failed'}, status_code=402)
        else:
            return JSONResponse({'ok': False, 'detail': 'Bad Request'}, status_code=400)
    else:
        if not settings.DEBUG and user.phone != settings.DEBUG_PHONE:
            user: models.User
            if user.phone:
                text = order_accept_send_sms(user.language, is_accept=False)
                response_message = await eskiz.send_sms(user.phone, text)
                return JSONResponse({
                    'ok': True, 'detail': 'Successfully Canceled',
                    'message': f'{response_message.message}'},
                    status_code=201)
        return JSONResponse({'ok': True, 'detail': 'Successfully Canceled'}, status_code=201)


@router.post('/change/order/status/{booking_id}/', )
async def update_order_status(
        booking_id: int,
        status: enums.BookingStatus,
        user: schemas.MerchantUser = Depends(deps.get_current_user),
):
    if not user.dashboard or not user.dashboard.default_property_id:
        return JSONResponse({'ok': False, 'detail': 'Must choose the main hotel'}, status_code=406)
    is_updated = await crud_booking.change_order_status(
        status=status,
        booking_id=booking_id,
        property_id=user.dashboard.default_property_id
    )
    if is_updated:
        return JSONResponse({'ok': True, 'detail': 'Successfully Updated'}, status_code=200)
    return JSONResponse({'ok': True, 'detail': 'Bad Request'}, status_code=400)


@router.get('/get/rooms/{room_id}/', response_model=List[schemas.Room], status_code=200,
            dependencies=[Depends(deps.get_current_user)])
async def get_empty_template_rooms(room_id: int, booked_from: date, booked_to: date):
    return await crud_booking.get_empty_template_rooms(room_id=room_id, booked_from=booked_from, booked_to=booked_to)


@router.get("/booking/history/", response_model=schemas.DataResponse[schemas.Booking])
async def booking_history(
        paginator: Paginator = Depends(paginate),
        q: str = Query(None),
        search_type: enums.SearchType = Query(None, alias='search_type'),
        sort_by: enums.HistorySortBy = Query(None, alias='sort_by'),
        sort_type: enums.SortType = Query('desc', alias='sort_type'),
        filter_by: enums.StatusBy = Query(None, alias='filter_by'),
        user: schemas.MerchantUser = Depends(deps.get_current_user)
):
    if not user.dashboard or not user.dashboard.default_property_id:
        return JSONResponse({'ok': False, 'detail': 'Must choose the main hotel'}, status_code=406)
    return await paginator.execute(
        crud_booking.merchant_booking_history(
            q=q,
            search_type=search_type,
            sort_by=sort_by,
            sort_type=sort_type,
            property_id=user.dashboard.default_property_id,
            filter_by=filter_by)
    )


@router.get("/booking/history/statistics/")
async def get_booking_statistics(
        user: schemas.MerchantUser = Depends(deps.get_current_user),
        days: CountByDays = CountByDays.LAST_30_DAYS):
    if not user.dashboard or not user.dashboard.default_property_id:
        return JSONResponse({'ok': False, 'detail': 'Must choose the main hotel'}, status_code=406)
    return await crud_booking.get_booking_statistics(days, property_id=user.dashboard.default_property_id)


@router.get("/order/history/", response_model=schemas.DataResponse[schemas.Booking])
async def order_history(
        paginator: Paginator = Depends(paginate),
        q: str = Query(None),
        search_type: enums.SearchType = Query(None, alias='search_type'),
        sort_type: enums.SortType = Query('desc', alias='sort_type'),
        sort_by: enums.HistorySortBy = Query(None, alias='sort_by'),
        filter_by: enums.OrderHistoryStatus = Query(None, alias='filter_by'),
        user: schemas.MerchantUser = Depends(deps.get_current_user)
):
    if not user.dashboard or not user.dashboard.default_property_id:
        return JSONResponse({'ok': False, 'detail': 'Must choose the main hotel'}, status_code=406)

    return await paginator.execute(crud_booking.order_history(
        q=q,
        search_type=search_type,
        sort_type=sort_type,
        filter_by=filter_by,
        property_id=user.dashboard.default_property_id,
        sort_by=sort_by)
    )
