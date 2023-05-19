import logging
import re
from datetime import datetime
from typing import List

import sqlalchemy as sa
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, selectinload
from sqlalchemy.sql import asc, desc
from sqlalchemy.sql import operators

from app import models
from app import schemas
from app.core.dependencies import get_db
from app.models import enums

logger = logging.getLogger(__name__)


async def create_property(added_by_id: int, property_in: schemas.PropertyCreate):
    db = get_db()
    try:
        property_instance = models.Property(added_by_id=added_by_id,
                                            **property_in.dict(
                                                exclude={
                                                    "rooms",
                                                    "services",
                                                    "translations",
                                                    "photos",
                                                    "languages"
                                                }
                                            ))
        await property_instance.save(refresh=True)

        await models.PropertyTranslation.bulk_create([
            models.PropertyTranslation(property_id=property_instance.id, **translation.dict())
            for translation in property_in.translations
        ])

        await models.PropertyPhoto.bulk_create([
            models.PropertyPhoto(property_id=property_instance.id, **photo.dict())
            for photo in property_in.photos
        ])

        await create_room_template(property_id=property_instance.id, room_templates=property_in.rooms)

        await models.PropertyService.bulk_create([
            models.PropertyService(property_id=property_instance.id, service_id=service.service_id,
                                   icon_id=await find_service_icon(service_name=service.service_name))

            for service in property_in.services
        ])

        await models.PropertyLanguage.bulk_create([
            models.PropertyLanguage(property_id=property_instance.id, language_id=language)
            for language in property_in.languages
        ])

        await db.commit()

        await db.refresh(property_instance)
        return property_instance
    except SQLAlchemyError as e:
        logger.error(e)
        await db.rollback()
        raise e


async def find_service_icon(service_name: str):
    db = get_db()
    try:
        service_icon_name = f"service_{re.sub('[^0-9a-zA-Z]+', '_', service_name.lower())}.png"
        service_icon = (
            await db.execute(
                sa.select(models.DocFile.id).where(
                    models.DocFile.name == f"{service_icon_name}"))
        ).scalar_one_or_none()
        return service_icon
    except Exception as e:
        logger.error(e)
        raise e


async def get_room_services_by_category_id(category_id: int):
    db = get_db()
    query = sa.select(models.ServiceCategory).join(
        models.Service, models.Service.category_id == models.ServiceCategory.id
    ).options(
        contains_eager(models.ServiceCategory.services)
    ).where(
        models.ServiceCategory.id == category_id,
        operators.is_(models.ServiceCategory.is_property_service_category, False)
    )
    result: list[models.ServiceCategory] = (await db.execute(query)).scalars().unique().all()
    return result


async def create_room_template(property_id: int, room_templates: List[schemas.RoomTemplateCreate]):
    db = get_db()
    try:
        for room in room_templates:
            room_instance = models.PropertyRoomTemplate(
                property_id=property_id,
                **room.dict(exclude={'numbers', 'photos', 'beds', 'services'})
            )
            await room_instance.save(refresh=True)

            await models.RoomPhoto.bulk_create([
                models.RoomPhoto(room_id=room_instance.id, **photo.dict())
                for photo in room.photos
            ])

            await models.PropertyRoom.bulk_create([
                models.PropertyRoom(room_id=room_instance.id, name=n, status=enums.RoomStatus.EMPTY)
                for n in room.numbers
            ])

            await models.RoomBed.bulk_create([
                models.RoomBed(room_id=room_instance.id, **bed.dict())
                for bed in room.beds
            ])
            await models.RoomService.bulk_create([
                models.RoomService(room_id=room_instance.id, service_id=service)
                for service in room.services
            ])
    except SQLAlchemyError as e:
        logger.error(e)
        await db.rollback()
        raise e


async def create_room_template_one_object(property_id: int, room: schemas.RoomTemplateCreate):
    db = get_db()
    try:
        room_instance = models.PropertyRoomTemplate(
            property_id=property_id,
            **room.dict(exclude={'numbers', 'photos', 'beds', 'services'})
        )
        await room_instance.save(refresh=True)

        rooms = await models.PropertyRoom.bulk_create([
            models.PropertyRoom(room_id=room_instance.id, name=n)
            for n in room.numbers
        ])

        await models.PropertyRoomStatus.bulk_create(
            [models.PropertyRoomStatus(
                property_room_id=r.id,
                status=enums.RoomStatus.EMPTY
            ) for r in rooms])

        await models.RoomPhoto.bulk_create([
            models.RoomPhoto(room_id=room_instance.id, **photo.dict())
            for photo in room.photos
        ])

        await models.RoomBed.bulk_create([
            models.RoomBed(room_id=room_instance.id, **bed.dict())
            for bed in room.beds
        ])
        await models.RoomService.bulk_create([
            models.RoomService(room_id=room_instance.id, service_id=service)
            for service in room.services
        ])
        await db.commit()
        await db.refresh(room_instance)
        return room_instance
    except Exception as e:
        logger.error(e)
        await db.rollback()
        raise e


def get_all_merchant_properties(added_by_id: int):
    query = sa.select(models.Property).options(
        sa.orm.noload(models.Property.city),
        sa.orm.noload(models.Property.photos),
        sa.orm.noload(models.Property.services),
        sa.orm.noload(models.Property.rating),
        sa.orm.noload(models.Property.rooms),
        sa.orm.noload(models.Property.languages)
    ).where(
        models.Property.added_by_id == added_by_id
    )
    return query


async def update_property_priority(added_by_id: int, property_id: int):
    db = get_db()
    dashboard = (
        await db.execute(
            sa.select(models.MerchantDashboard
                      ).where(models.MerchantDashboard.id == added_by_id
                              )
        )).scalar_one_or_none()
    if dashboard:
        dashboard.default_property_id = property_id
        db.add(dashboard)
        await db.commit()
        await db.refresh(dashboard)
        return True
    return False


async def property_room_template_services(room_id: int, is_client: bool = False):
    db = get_db()
    query = sa.select(models.ServiceCategory).join(
        models.Service, models.Service.category_id == models.ServiceCategory.id
    ).options(
        contains_eager(models.ServiceCategory.services)
    ).join(
        models.RoomService, models.Service.id == models.RoomService.service_id
    ).where(
        models.RoomService.room_id == room_id
    )
    if is_client:
        return query
    return (await db.execute(query)).scalars().unique().all()


async def property_get_by_id(property_id: int, checkin: datetime, checkout: datetime) -> schemas.Property | None:
    db = get_db()
    query = sa.select(models.Property)

    subquery = sa.select(models.PropertyRoomStatus.property_room_id).where(
        models.PropertyRoomStatus.status_from >= checkin.date(),
        models.PropertyRoomStatus.status_until <= checkout.date(),
    ).where(
        models.PropertyRoomStatus.property_room_id != None
    )

    query = query.join(
        models.PropertyRoomTemplate, models.Property.id == models.PropertyRoomTemplate.property_id
    ).join(
        models.PropertyRoom,
        models.PropertyRoomTemplate.id == models.PropertyRoom.room_id
    ).where(
        ~operators.in_op(models.PropertyRoom.id, subquery)
    ).where(
        models.Property.id == property_id,
        models.Property.is_active == enums.PropertyStatus.ACTIVE,
        models.PropertyRoomTemplate.is_deleted == False,
    )

    return (await db.execute(query)).scalar()


async def get_properties_by_criteria(
        q: str,
        sort_by: enums.PropertySortBy,
        sort_type: enums.SortType,
        breakfast: bool,
        property_type: List[int],
        star_rating: List[enums.PropertyStarRating],
        city: str,
        city_centre_distance: List[enums.CityCentreDistance],
        services: List[int],

        price_gte: int,
        price_lte: int,
        checkin: datetime,
        checkout: datetime,
        rooms: int,
        adults: int,
        is_resident: bool,
        children: int,
        ratings: List[int],
        page: int = 1,
        per_page: int = 10
):
    db = get_db()
    query = sa.select(models.Property)
    if q:
        query = query.where(
            operators.ilike_op(models.Property.name, f"%{q}%")
        )
    if property_type:
        query = query.where(
            operators.in_op(models.Property.type_id, property_type)
        )
    if city:
        subquery = sa.select(models.Property.id).join(
            models.City, models.City.id == models.Property.city_id
        ).where(
            models.City.name_slug == city
        )
        query = query.where(
            operators.in_op(models.Property.id, subquery)
        )
    if services:
        subquery = sa.select(models.PropertyService.property_id).where(
            operators.in_op(models.PropertyService.service_id, services)
        )
        query = query.where(
            operators.in_op(models.Property.id, subquery)
        )
    if star_rating:
        query = query.where(
            models.Property.star_rating.in_([r.value for r in star_rating])
        )
    if breakfast:
        query = query.where(
            models.Property.is_breakfast_served == True
        )
    if ratings:
        ratings.sort()
        max_rating = [6, 9, 10][len(ratings) - 1] if len(ratings) >= 3 else 10
        subquery = sa.select(models.PropertyRating.property_id).where(
            operators.between_op(models.PropertyRating.avg, 0, max_rating)
        )
        query = query.where(
            operators.in_op(models.Property.id, subquery)
        )

    if rooms:
        subquery = sa.select(
            models.PropertyRoomTemplate.property_id
        ).where(
            models.PropertyRoomTemplate.number_of_rooms >= rooms,
            models.PropertyRoomTemplate.is_deleted == False
        ).join(
            models.PropertyRoom,
            models.PropertyRoomTemplate.id == models.PropertyRoom.room_id
        ).group_by(
            models.PropertyRoomTemplate.property_id
        )

        query = query.where(
            operators.in_op(models.Property.id, subquery)
        )

    if adults:
        subquery = sa.select(models.PropertyRoomTemplate.property_id).where(
            models.PropertyRoomTemplate.max_number_of_guests >= adults
        ).group_by(
            models.PropertyRoomTemplate.property_id
        )

        query = query.where(
            operators.in_op(models.Property.id, subquery)
        )

    if is_resident:
        # TODO: add filtering by residency status
        pass

    if children:
        subquery = sa.select(models.PropertyRoomTemplate.property_id).where(
            models.PropertyRoomTemplate.max_number_of_children >= children
        ).group_by(
            models.PropertyRoomTemplate.property_id
        )

        query = query.where(
            operators.in_op(models.Property.id, subquery)
        )

    if sort_by.RATING:
        query = query.outerjoin(
            models.PropertyRating, models.PropertyRating.property_id == models.Property.id, full=True
        )

    subquery = sa.select(models.PropertyRoomStatus.property_room_id).where(
        models.PropertyRoomStatus.status_from >= checkin.date(),
        models.PropertyRoomStatus.status_until <= checkout.date(),
    ).where(
        models.PropertyRoomStatus.property_room_id != None
    )

    query = query.join(
        models.PropertyRoomTemplate,
        models.PropertyRoomTemplate.property_id == models.Property.id
    ).join(
        models.PropertyRoom, models.PropertyRoom.room_id == models.PropertyRoomTemplate.id
    ).where(
        ~operators.in_op(models.PropertyRoom.id, subquery)
    ).where(
        models.Property.is_active == enums.PropertyStatus.ACTIVE
    ).where(
        operators.between_op(models.PropertyRoomTemplate.price, price_gte, price_lte)
    ).where(
        models.PropertyRoomTemplate.is_deleted == False
    )

    query = filter_by_sort_type(query, sort_type, sort_by, is_resident)
    query = filter_by_city_distance(query, city_centre_distance)

    results: List[schemas.Property] = (await db.execute(query)).scalars().unique().all()
    return multiple_(paginate(results, page, per_page, rooms), rooms), len(results)


def paginate(results, page, per_page, rooms: int = 1):
    skip = (page - 1) * per_page
    return multiple_(results[skip: skip + per_page], rooms)


def multiple_(results, rooms: int = 1):
    results_ = []
    for result in results:
        result: schemas.Property.from_orm(result)
        result.minimum_price_per_night = result.minimum_price_per_night * rooms
        result.minimum_price_per_night_for_resident = result.minimum_price_per_night_for_resident * rooms
        results_.append(result)
    return results_


def get_property_types():
    query = sa.select(models.PropertyType)
    return query


def filter_by_city_distance(query, city_centre_distance):
    if city_centre_distance:
        if city_centre_distance == enums.CityCentreDistance.ONE_THREE:
            query = query.where(
                models.Property.city_centre_distance >= 1, models.Property.city_centre_distance <= 3
            )
        elif city_centre_distance == enums.CityCentreDistance.FOUR_SIX:
            query = query.where(
                models.Property.city_centre_distance >= 4, models.Property.city_centre_distance <= 6
            )
        else:
            query = query.where(
                models.Property.city_centre_distance >= 7
            )
    return query


def filter_by_sort_type(query, sort_type, sort_by, is_resident: bool = False):
    sort_type_ = desc if sort_type == enums.SortType.DESC else asc
    if sort_by:
        if sort_by == enums.PropertySortBy.NEWEST:
            query = query.order_by(sort_type_(models.Property.id))
        elif sort_by == enums.PropertySortBy.PRICE:
            if is_resident:
                query = query.order_by(sort_type_(models.Property.minimum_price_per_night_for_resident))
            query = query.order_by(sort_type_(models.Property.minimum_price_per_night))
        elif sort_by == enums.PropertySortBy.DISCOUNT:
            query = query.order_by(sort_type_(models.PropertyRoomTemplate.price_has_discount))
    return query


async def create_property_room_type(db: AsyncSession, type_: str):
    instance = models.RoomType(type=type_)
    db.add(instance)
    await db.commit()
    await db.refresh(instance)
    return instance


async def create_property_room_names(db: AsyncSession, type_id: int, names: List[str]):
    for name in names:
        instance = models.RoomName(type_id=type_id, name=name)
        db.add(instance)
    if names:
        await db.commit()


def get_saved_filters():
    return sa.select(models.SavedFilter).order_by('id')


def get_services():
    return sa.select(models.Service).join(
        models.ServiceCategory, models.ServiceCategory.id == models.Service.category_id
    ).where(
        operators.is_(models.ServiceCategory.is_property_service_category, True)
    )


def get_languages():
    query = sa.select(models.Language)
    return query


def get_room_types():
    query = sa.select(models.RoomType)
    return query


def get_bed_types():
    query = sa.select(models.BedType)
    return query


def get_room_services():
    query = sa.select(models.ServiceCategory).options(
        selectinload(models.ServiceCategory.services)
    ).where(
        operators.is_(models.ServiceCategory.is_property_service_category, False)
    )
    return query


async def create_or_update_room_template_services(room_id: int, services: list[int]):
    db = get_db()
    if services:
        await db.execute(sa.delete(models.RoomService).where(models.RoomService.room_id == room_id))
        await db.commit()
        await models.RoomService.bulk_create([
            models.RoomService(room_id=room_id, service_id=service_id) for service_id in services]
        )
        await db.commit()
        return True
    return False


def get_property_photos(property_id: int):
    query = sa.select(models.PropertyPhoto).where(
        models.PropertyPhoto.property_id == property_id
    )
    return query


async def create_property_photo(
        property_id: int,
        photo_in: schemas.PhotoCreate):
    db = get_db()
    photo = models.PropertyPhoto(property_id=property_id, **photo_in.dict())
    if photo:
        db.add(photo)
        await db.commit()
        return True
    return False


async def create_room_bed(room_id: int, beds_in: List[schemas.RoomBedCreate]):
    db = get_db()
    try:
        if beds_in:
            await db.execute(sa.delete(models.RoomBed).where(models.RoomBed.room_id == room_id))
            await models.RoomBed.bulk_create([models.RoomBed(room_id=room_id, **bed_in.dict()) for bed_in in beds_in])
            await db.commit()
            return True
        return False
    except Exception as e:
        logger.error(e)
        await db.rollback()
        raise e


def get_room_beds(room_id: int):
    query = sa.select(models.RoomBed).where(
        models.RoomBed.room_id == room_id
    )
    return query


async def delete_property_photo(property_photo_id: int):
    db = get_db()
    photo = (
        await db.execute(
            sa.select(models.PropertyPhoto).where(models.PropertyPhoto.id == property_photo_id)
        )).scalar_one_or_none()
    if photo:
        await db.execute(sa.delete(models.PropertyPhoto).where(
            models.PropertyPhoto.id == property_photo_id
        ))
        await db.commit()
        return True
    return False


async def get_property_settings(added_by_id: int, property_id: int) -> schemas.PropertySettings | None:
    db = get_db()
    query = sa.select(models.Property).where(
        models.Property.added_by_id == added_by_id,
        models.Property.id == property_id,
    )
    result = (await db.execute(query)).scalar_one_or_none()

    return result


async def update_property_settings(added_by_id: int, default_property_id: int,
                                   property_in: schemas.PropertySettingsUpdate):
    db = get_db()
    property_obj = await get_property_settings(added_by_id, default_property_id)
    if property_obj:
        update_stmt = (sa.update(
            models.Property
        ).where(
            models.Property.added_by_id == added_by_id,
            models.Property.id == property_obj.id
        ).values(
            **property_in.dict(exclude={"translations"})
        ))
        update_translation_stmt = (sa.update(
            models.PropertyTranslation
        ).where(
            models.PropertyTranslation.property_id == property_obj.id
        ))

        params = [
            {
                'language': tr.language,
                'description': tr.description,
                'address': tr.address
            }
            for tr in property_in.translations
        ]

        await db.execute(update_stmt, params)
        await db.execute(update_translation_stmt)
        await db.commit()
        return True
    return False


async def get_room_templates(property_id: int, page: int = 1, per_page: int = 10) -> \
        tuple[List[schemas.RoomTemplateWithRooms], int]:
    today = datetime.utcnow()
    db = get_db()
    query = sa.select(models.PropertyRoomTemplate).where(
        models.PropertyRoomTemplate.property_id == property_id,
        operators.is_(models.PropertyRoomTemplate.is_deleted, False)
    )
    total = (await db.execute(sa.select(sa.func.count()).select_from(query))).scalar()
    results = (await db.execute(query.offset((page - 1) * per_page).limit(per_page))).scalars().unique().all()

    rooms = (
        await db.execute(
            sa.select(models.PropertyRoom).where(operators.in_op(models.PropertyRoom.room_id, [r.id for r in results])))
    ).scalars().unique().all()
    statuses = (
        await db.execute(sa.select(models.PropertyRoomStatus).where(
            models.PropertyRoomStatus.status_from == today.date()
        ))).scalars().unique().all()

    statuses_dict = {s.property_room_id: s for s in statuses}

    rooms_ = {}
    for room in rooms:
        if room.id in statuses_dict:
            room.status = statuses_dict[room.id].status
        else:
            room.status = enums.RoomStatus.EMPTY
        rooms_[room.id] = room

    for result in results:
        result_rooms = [r for r in result.rooms if r.id in rooms_]
        result = schemas.RoomTemplateWithRooms.from_orm(result)
        result.rooms = result_rooms
    return results, total


async def get_room_template(room_id: int, property_id: int):
    db = get_db()
    query = sa.select(models.PropertyRoomTemplate).where(
        models.PropertyRoomTemplate.id == room_id,
        models.PropertyRoomTemplate.property_id == property_id,
        operators.is_(models.PropertyRoomTemplate.is_deleted, False)
    )
    return (await db.execute(query)).scalar_one_or_none()


async def update_room_status(room_id: int, obj_in: schemas.RoomStatusUpdate):
    db = get_db()
    try:
        room: models.PropertyRoom = (await db.execute(
            sa.select(models.PropertyRoom).where(models.PropertyRoom.id == room_id))).scalar_one_or_none()
        if room:
            room.status = obj_in.status
            await db.commit()
            return True
        return False
    except Exception as e:
        logger.error(e)
        await db.rollback()
        raise e


def get_room_statuses(room_id: int):
    query = sa.select(models.PropertyRoomStatus).where(
        models.PropertyRoomStatus.property_room_id == room_id,
        models.PropertyRoomStatus.status_from >= datetime.utcnow().date()
    ).order_by(models.PropertyRoomStatus.status_from)

    return query


async def create_or_update_room_status(room_id: int, obj_in: List[schemas.RoomStatusByDay]):
    db = get_db()
    try:
        if obj_in:
            query = sa.delete(models.PropertyRoomStatus).where(
                models.PropertyRoomStatus.property_room_id == room_id,
                models.PropertyRoomStatus.status == enums.RoomStatus.BUSY,
                models.PropertyRoomStatus.is_disabled == False,
                operators.in_op(
                    models.PropertyRoomStatus.status_from,
                    [x.status_from for x in obj_in if x.for_delete]
                )
            )
            await db.execute(query)
            obj_in = [x for x in obj_in if not x.for_delete]
            await models.PropertyRoomStatus.bulk_create([
                models.PropertyRoomStatus(
                    property_room_id=room_id,
                    status=enums.RoomStatus.BUSY,
                    status_from=obj.status_from,
                    status_until=obj.status_from,
                    is_disabled=False
                ) for obj in obj_in
            ])
            await db.commit()
            return True
        return False
    except Exception as e:
        logger.error(e)
        await db.rollback()
        raise e


async def update_property_room_template_rooms(
        room_id: int,
        numbers: list[str]):
    db = get_db()
    try:
        if numbers:
            await db.execute(sa.delete(models.PropertyRoom).where(models.PropertyRoom.room_id == room_id))
            rooms = await models.PropertyRoom.bulk_create([
                models.PropertyRoom(room_id=room_id, name=n)
                for n in numbers
            ])
            await models.PropertyRoomStatus.bulk_create([
                models.PropertyRoomStatus(property_room_id=r.id, status=enums.RoomStatus.EMPTY) for r in rooms
            ])
    except Exception as e:
        logger.error(e)
        await db.rollback()
        raise e


async def create_room_photos(room_id: int, photos: list[schemas.PhotoCreate]):
    db = get_db()
    try:
        if photos:
            await db.execute(sa.delete(models.RoomPhoto).where(models.RoomPhoto.room_id == room_id))
            await models.RoomPhoto.bulk_create([models.RoomPhoto(room_id=room_id, **photo.dict()) for photo in photos])
    except Exception as e:
        logger.error(e)
        await db.rollback()
        raise e


async def update_property_room_template(room_id: int, obj_in: schemas.RoomTemplateUpdate):
    db = get_db()
    try:
        room = (
            await db.execute(sa.select(models.PropertyRoomTemplate).where(
                models.PropertyRoomTemplate.id == room_id))).scalar_one_or_none()
        if room:
            room: models.PropertyRoomTemplate
            await room.update_attrs(**obj_in.dict(exclude={
                "beds",
                "photos",
                "numbers",
            }))

            await create_room_bed(room_id=room.id, beds_in=obj_in.beds)
            await update_property_room_template_rooms(room_id=room.id, numbers=obj_in.numbers)
            await create_room_photos(room_id=room.id, photos=obj_in.photos)
            await db.commit()
            return True
        return False
    except Exception as e:
        logger.error(e)
        await db.rollback()
        raise e


async def delete_property_room_template(room_id: int):
    db = get_db()
    room = (
        await db.execute(
            sa.select(models.PropertyRoomTemplate).where(
                models.PropertyRoomTemplate.id == room_id,
                models.PropertyRoomTemplate.is_deleted == False
            ))
    ).scalar_one_or_none()
    if room:
        room.is_deleted = True
        await db.commit()
        return True
    return False
