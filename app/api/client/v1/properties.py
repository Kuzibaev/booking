from datetime import datetime, timedelta, date
from typing import List

import pytz
from fastapi import APIRouter, Depends, Query
from pydantic import parse_obj_as
from starlette.responses import JSONResponse

from app import schemas
from app.core.conf import settings
from app.crud import crud_property, crud_booking
from app.models import enums
from app.utils.paginator import paginate, Paginator

router = APIRouter()


@router.get('/get-services/', response_model=schemas.DataResponse[schemas.Service])
async def get_services(paginator: Paginator = Depends(paginate)):
    return await paginator.execute(crud_property.get_services())


@router.get('/filters/', response_model=schemas.DataResponse[schemas.SavedFilter])
async def saved_filter_list(paginator: Paginator = Depends(paginate)):
    return await paginator.execute(crud_property.get_saved_filters())


@router.get('/type/list/', response_model=schemas.DataResponse[schemas.PropertyType])
async def get_property_types(paginator: Paginator = Depends(paginate)):
    return await paginator.execute(crud_property.get_property_types())


@router.get("/list/", status_code=200)
async def get_properties(
        q: str = Query(None),
        page: int = Query(1, alias='page'),
        per_page: int = Query(10, alias='per_page'),
        sort_by: enums.PropertySortBy = Query(alias='sort-by'),
        sort_type: enums.SortType = Query('asc', alias='sort-type'),
        breakfast: bool = Query(None),
        property_type: List[int] = Query(None, alias='type'),
        star_rating: List[enums.PropertyStarRating] = Query(None, alias='star-rating'),
        city_centre_distance: List[enums.CityCentreDistance] = Query(None, alias='city-centre-distance'),
        services: List[int] = Query(None, alias='service'),
        price_gte: int = Query(0, alias="price-gte"),
        price_lte: int = Query(999_999_999, alias="price-lte"),

        city: str = Query(None),
        checkin: datetime = Query(datetime.now(tz=pytz.timezone(settings.TIMEZONE))),
        checkout: datetime = Query(datetime.now(tz=pytz.timezone(settings.TIMEZONE)) + timedelta(days=1)),
        rooms: int = Query(1),
        adults: int = Query(1),
        children: int = Query(None),
        is_resident: bool = Query(default=True),
        ratings: List[int] = Query(None, alias='ratings', ge=0, le=10),

):
    results, total = await crud_property.get_properties_by_criteria(
        q=q,
        sort_by=sort_by,
        sort_type=sort_type,
        breakfast=breakfast,
        property_type=property_type,
        star_rating=star_rating,
        city_centre_distance=city_centre_distance,
        services=services,
        price_gte=price_gte,
        price_lte=price_lte,
        city=city,
        checkin=checkin,
        checkout=checkout,
        rooms=rooms,
        adults=adults,
        is_resident=is_resident,
        children=children,
        ratings=ratings,
        page=page,
        per_page=per_page
    )
    return schemas.DataResponse(items=parse_obj_as(List[schemas.Property], results), total=total)


@router.get('/{property_id}/', response_model=schemas.Property, status_code=200)
async def get_property_by_id(property_id: int,
                             checkin: datetime = Query(datetime.now(tz=pytz.timezone(settings.TIMEZONE))),
                             checkout: datetime = Query(
                                 datetime.now(tz=pytz.timezone(settings.TIMEZONE)) + timedelta(days=1)),
                             ):
    if result := await crud_property.property_get_by_id(property_id=property_id, checkin=checkin, checkout=checkout):
        return result
    return JSONResponse({'ok': True, 'detail': 'Not Found'}, status_code=404)


@router.get('/property-room-template/{property_template_id}/services/',
            response_model=schemas.DataResponse[schemas.ServiceCategory])
async def property_room_template_services(
        property_template_id: int,
        paginator: Paginator = Depends(paginate)
):
    return await paginator.execute(
        await crud_property.property_room_template_services(room_id=property_template_id, is_client=True))


@router.get('/get/rooms/{room_id}/', )
async def get_empty_template_rooms(room_id: int, booked_from: date, booked_to: date):
    total = await crud_booking.get_empty_template_rooms(
        room_id=room_id, booked_from=booked_from, booked_to=booked_to,
        is_client=True
    )
    return dict(total=total)
