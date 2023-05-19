from typing import Optional, List

import sqlalchemy as sa
from fastapi import APIRouter, Depends, Query
from pydantic import parse_obj_as
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from app import schemas, models
from app.api import deps
from app.crud import crud_property, crud_city

from app.utils.paginator import Paginator, paginate

router = APIRouter()


@router.get('/all-lang/', response_model=schemas.DataResponse[schemas.Language], status_code=status.HTTP_200_OK)
async def get_languages(paginator: Paginator = Depends(paginate)):
    return await paginator.execute(crud_property.get_languages())


@router.get('/city/list/', response_model=schemas.DataResponse[schemas.City], status_code=status.HTTP_200_OK)
async def get_cities(paginator: Paginator = Depends(paginate)):
    return await paginator.execute(crud_city.get_multi())


@router.get('/get-services/', response_model=schemas.DataResponse[schemas.Service], status_code=status.HTTP_200_OK)
async def get_services(paginator: Paginator = Depends(paginate)):
    return await paginator.execute(crud_property.get_services())


@router.get('/room-types/', response_model=schemas.DataResponse[schemas.BaseRoomType], status_code=status.HTTP_200_OK)
async def get_room_types(paginator: Paginator = Depends(paginate)):
    return await paginator.execute(crud_property.get_room_types())


@router.get('/room-services/', response_model=schemas.DataResponse[schemas.ServiceCategory],
            status_code=status.HTTP_200_OK)
async def get_room_services(paginator: Paginator = Depends(paginate)):
    return await paginator.execute(crud_property.get_room_services())


@router.get('/type/list/', response_model=schemas.DataResponse[schemas.PropertyType], status_code=status.HTTP_200_OK)
async def get_property_types(paginator: Paginator = Depends(paginate)):
    return await paginator.execute(crud_property.get_property_types())


@router.get('/bed-types/', response_model=schemas.DataResponse[schemas.BedType], status_code=status.HTTP_200_OK)
async def get_bed_types(paginator: Paginator = Depends(paginate)):
    return await paginator.execute(crud_property.get_bed_types())


@router.post('/create/', response_model=Optional[schemas.Property])
async def create_property(property_in: schemas.PropertyCreate,
                          user: schemas.MerchantUser = Depends(deps.is_chief)):
    property_ = await crud_property.create_property(property_in=property_in, added_by_id=user.dashboard.id)
    if property_:
        return JSONResponse({'ok': True, 'detail': 'Successfully Created', 'property_id': property_.id},
                            status_code=status.HTTP_201_CREATED)
    return JSONResponse({'ok': False, 'detail': 'Bad Request'}, status_code=status.HTTP_400_BAD_REQUEST)


@router.get('/get/all/property', response_model=schemas.DataResponse[schemas.PropertyEasy], status_code=200)
async def get_all_properties(
        paginator: Paginator = Depends(paginate),
        user: schemas.MerchantUser = Depends(deps.get_current_user)):
    return await paginator.execute(crud_property.get_all_merchant_properties(added_by_id=user.dashboard.id))


@router.put('/update/property/priority/{property_id}/')
async def update_property_priority(property_id: int,
                                   user: schemas.MerchantUser = Depends(deps.get_current_user)):
    result = await crud_property.update_property_priority(added_by_id=user.dashboard.id, property_id=property_id)
    if result:
        return JSONResponse({'ok': True, 'detail': 'Successfully Updated'}, status_code=status.HTTP_200_OK)
    return JSONResponse({'ok': False, 'detail': 'Bad Request'}, status_code=status.HTTP_400_BAD_REQUEST)


@router.get('/photos/', response_model=schemas.DataResponse[schemas.PropertyPhoto])
async def get_property_photos(user: schemas.MerchantUser = Depends(deps.get_current_user),
                              paginator: Paginator = Depends(paginate)):
    if not user.dashboard or not user.dashboard.default_property_id:
        return JSONResponse({'ok': False, 'detail': 'Must choose the main hotel'}, status_code=406)
    return await paginator.execute(crud_property.get_property_photos(user.dashboard.default_property_id))


@router.post('/photo/create/')
async def create_property_photo(
        photo_in: schemas.PhotoCreate,
        user: schemas.MerchantUser = Depends(deps.is_chief)
):
    if not user.dashboard or not user.dashboard.default_property_id:
        return JSONResponse({'ok': False, 'detail': 'Must choose the main hotel'}, status_code=406)

    is_created = await crud_property.create_property_photo(
        property_id=user.dashboard.default_property_id,
        photo_in=photo_in
    )
    if is_created:
        return JSONResponse({'ok': True, 'detail': 'Successfully Created'}, status_code=status.HTTP_201_CREATED)
    return JSONResponse({'ok': False, 'detail': 'Bad Request'}, status_code=status.HTTP_400_BAD_REQUEST)


@router.delete('/photo/delete/{property_photo_id}/')
async def delete_property_photo(property_photo_id: int,
                                user: schemas.MerchantUser = Depends(deps.is_chief)):
    if not user.dashboard or not user.dashboard.default_property_id:
        return JSONResponse({'ok': False, 'detail': 'Must choose the main hotel'}, status_code=406)
    is_deleted = await crud_property.delete_property_photo(
        property_photo_id=property_photo_id
    )
    if is_deleted:
        return JSONResponse({'ok': True, 'detail': 'Successfully Deleted'}, status_code=status.HTTP_200_OK)
    return JSONResponse({'ok': False, 'detail': 'Bad Request'}, status_code=status.HTTP_400_BAD_REQUEST)


@router.get('/settings/', response_model=Optional[schemas.PropertySettings])
async def get_settings(user: schemas.MerchantUser = Depends(deps.is_chief)):
    if not user.dashboard or not user.dashboard.default_property_id:
        return JSONResponse({'ok': False, 'detail': 'Must choose the main hotel'}, status_code=406)
    if result := await crud_property.get_property_settings(
            added_by_id=user.dashboard.id,
            property_id=user.dashboard.default_property_id
    ):
        return result
    return JSONResponse({'ok': False, 'detail': 'Bad Request'}, status_code=status.HTTP_400_BAD_REQUEST)


@router.post('/update/settings/')
async def update_settings(
        property_in: schemas.PropertySettingsUpdate,
        user: schemas.MerchantUser = Depends(deps.is_chief),
):
    if not user.dashboard or not user.dashboard.default_property_id:
        return JSONResponse({'ok': False, 'detail': 'Must choose the main hotel'}, status_code=406)
    is_updated = await crud_property.update_property_settings(
        added_by_id=user.dashboard.id,
        property_in=property_in,
        default_property_id=user.dashboard.default_property_id)
    if is_updated:
        return JSONResponse({'ok': True, 'detail': 'Successfully Updated'}, status_code=status.HTTP_200_OK)
    return JSONResponse({'ok': False, 'detail': 'Bad Request'}, status_code=status.HTTP_400_BAD_REQUEST)


@router.get('/room-templates/list/', status_code=200)
async def get_property_room_templates(
        page: int = Query(1, alias='page'),
        per_page: int = Query(10, alias='per_page'),
        user: schemas.MerchantUser = Depends(deps.get_current_user),
):
    if not user.dashboard or not user.dashboard.default_property_id:
        return JSONResponse({'ok': False, 'detail': 'Must choose the main hotel'}, status_code=406)
    results, total = await crud_property.get_room_templates(
        property_id=user.dashboard.default_property_id,
        page=page,
        per_page=per_page
    )
    return schemas.DataResponse(items=parse_obj_as(List[schemas.RoomTemplateWithRooms], results), total=total)


@router.get('/room-template/{room_id}/', response_model=schemas.RoomTemplateWithRooms)
async def get_property_room_template(room_id: int, user: schemas.MerchantUser = Depends(deps.get_current_user)):
    if room := await crud_property.get_room_template(
            room_id=room_id,
            property_id=user.dashboard.default_property_id
    ):
        return room
    return JSONResponse({'ok': True, 'detail': 'Not Found'}, status_code=404)


@router.post('/room-status/{room_id}/', dependencies=[Depends(deps.get_current_user)])
async def update_room_status(
        room_id: int, obj_in: schemas.RoomStatusUpdate
):
    is_updated = await crud_property.update_room_status(room_id=room_id, obj_in=obj_in)
    if is_updated:
        return JSONResponse({'ok': False, 'detail': 'Successfully Created'}, status_code=201)
    return JSONResponse({'ok': False, 'detail': 'Bad Request'}, status_code=400)


@router.post('/room-busy-statuses/{room_id}/', dependencies=[Depends(deps.get_current_user)])
async def create_or_update_room_status(room_id: int, obj_in: List[schemas.RoomStatusByDay]):
    is_created = await crud_property.create_or_update_room_status(room_id, obj_in)
    if is_created:
        return JSONResponse({'ok': False, 'detail': 'Successfully Created'}, status_code=201)
    return JSONResponse({'ok': False, 'detail': 'Bad Request'}, status_code=400)


@router.get('/room-statuses/{room_id}/', dependencies=[Depends(deps.get_current_user)],
            response_model=schemas.DataResponse[schemas.RoomStatus])
async def get_room_statues(room_id: int, paginator: Paginator = Depends(paginate)):
    return await paginator.execute(crud_property.get_room_statuses(room_id=room_id))


@router.post('/room-template/post/', )
async def create_property_room_template(
        room_in: schemas.RoomTemplateCreate,
        user: schemas.MerchantUser = Depends(deps.is_chief)
):
    if not user.dashboard or not user.dashboard.default_property_id:
        return JSONResponse({'ok': False, 'detail': 'Must choose the main hotel'}, status_code=406)
    room = await crud_property.create_room_template_one_object(
        property_id=user.dashboard.default_property_id,
        room=room_in)
    if room:
        return JSONResponse({'ok': False, 'detail': 'Successfully Created'}, status_code=201)
    return JSONResponse({'ok': False, 'detail': 'Bad Request'}, status_code=status.HTTP_400_BAD_REQUEST)


@router.put('/room-template/update/{room_id}/', dependencies=[Depends(deps.is_chief)])
async def update_property_room_template(
        room_id: int,
        obj_in: schemas.RoomTemplateUpdate
):
    is_updated = await crud_property.update_property_room_template(room_id=room_id, obj_in=obj_in)
    if is_updated:
        return JSONResponse({'ok': True, 'detail': 'Successfully Updated'}, status_code=200)
    return JSONResponse({'ok': True, 'detail': 'Bad Request'}, status_code=400)


@router.delete('/room-template/delete/{room_id}/',
               dependencies=[Depends(deps.is_chief)])
async def delete_property_room_template(room_id: int):
    result = await crud_property.delete_property_room_template(room_id=room_id)
    if result:
        return JSONResponse({'ok': False, 'detail': 'Successfully Deleted'}, status_code=status.HTTP_200_OK)
    return JSONResponse({'ok': False, 'detail': 'Bad Request'}, status_code=status.HTTP_400_BAD_REQUEST)


@router.get('/property-room-template-services/{room_id}/', response_model=dict[str, list[schemas.ServiceCategory]],
            dependencies=[Depends(deps.get_current_user)], status_code=200)
async def property_room_template_services(room_id: int, db: AsyncSession = Depends(deps.get_db)):
    results = (await db.execute(
        sa.select(models.ServiceCategory).where(
            models.ServiceCategory.is_property_service_category == False))).scalars().unique().all()
    count_ = {r.id: len(r.services) for r in results}
    results_: list[schemas.ServiceCategory] = await crud_property.property_room_template_services(room_id=room_id)
    for r_ in results_:
        r_.count = count_.get(r_.id, 0)
    return dict(items=results_)


@router.post('/property-room-template-service/{room_id}/', dependencies=[Depends(deps.get_current_user)])
async def create_or_update_room_template_services(room_id: int, services: list[int]):
    result = await crud_property.create_or_update_room_template_services(room_id, services)
    if result:
        return JSONResponse({'ok': True, 'detail': 'Successfully Created'}, status_code=status.HTTP_201_CREATED)
    return JSONResponse({'ok': False, 'detail': 'Bad Request'}, status_code=status.HTTP_400_BAD_REQUEST)


@router.get('/room-template/beds/{room_id}/', dependencies=[Depends(deps.is_chief)],
            response_model=schemas.DataResponse[schemas.RoomTemplateBed], status_code=200)
async def get_room_template_beds(room_id: int, paginator: Paginator = Depends(paginate)):
    return await paginator.execute(crud_property.get_room_beds(room_id=room_id))


@router.post('/room-template/beds/update/{room_id}/', dependencies=[Depends(deps.is_chief)])
async def create_room_template_bed(room_id: int, obj_in: list[schemas.RoomBedCreate]):
    is_updated = await crud_property.create_room_bed(room_id, beds_in=obj_in)
    if is_updated:
        return JSONResponse({'ok': True, 'detail': 'Successfully Updated'}, status_code=status.HTTP_200_OK)
    return JSONResponse({'ok': False, 'detail': 'Bad Request'}, status_code=status.HTTP_400_BAD_REQUEST)
