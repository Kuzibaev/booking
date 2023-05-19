import logging
from datetime import datetime, timedelta, date

import sqlalchemy as sa
from sqlalchemy import func, desc, asc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import operators
from app import models
from app import schemas
from app.core.conf import settings
from app.core.dependencies import get_db
from app.models import enums

logger = logging.getLogger(__name__)


def get_all_bookings(user_id: int):
    query = sa.select(models.Booking).where(
        models.Booking.user_id == user_id
    ).where(
        models.Booking.status != enums.BookingStatus.CANCELED,
        models.Booking.status != enums.BookingStatus.CLOSED,
    )

    return query.order_by(models.Booking.id.desc())


async def get_booking(booking_id: int, user_id: int) -> schemas.Booking | None:
    db = get_db()
    stmt = sa.select(models.Booking).where(
        models.Booking.id == booking_id,
        models.Booking.user_id == user_id
    )
    booking = (await db.execute(stmt)).scalar_one_or_none()

    return booking


def make_booking_response(booking: schemas.Booking):
    count_property_room_template = {}

    for room in booking.rooms:
        count_property_room_template[
            (
                room.property_room_template_id,
                room.price,
                room.number_of_people
            )] = 1 + count_property_room_template.get(
            (room.property_room_template_id, room.price, room.number_of_people), 0)
    for room in booking.rooms:
        room.count = count_property_room_template.get(
            (room.property_room_template_id, room.price, room.number_of_people), 0)

    rooms = []
    for room in booking.rooms:
        if (room.property_room_template_id, room.price, room.number_of_people) not in [
            (r.property_room_template_id, r.price, r.number_of_people) for r in rooms]:
            rooms.append(room)
    booking.rooms = rooms

    return booking


async def get_booking_(booking_id: int, property_id: int):
    db = get_db()
    stmt = sa.select(models.Booking).where(
        models.Booking.id == booking_id,
        models.Booking.property_id == property_id
    )

    return (await db.execute(stmt)).scalar_one_or_none()


def get_booking_history(user_id: int):
    query = sa.select(models.Booking).where(
        models.Booking.user_id == user_id
    ).where(
        models.Booking.status != enums.BookingStatus.PENDING,
        models.Booking.status != enums.BookingStatus.CONFIRMED,
        models.Booking.status != enums.BookingStatus.ACTIVE,
    ).order_by(models.Booking.id.desc())

    return query


def _calculate_discount(price: float, from_: datetime | None, to: datetime | None, unit: enums.BillingUnit,
                        amount: float):
    now = settings.datetime

    if (from_ is not None and from_ <= now <= to) or from_ is None:
        if unit == enums.BillingUnit.FIXED_VALUE:
            price -= amount
        else:
            price -= price * amount / 100

    return price


def calculate_price(room: schemas.RoomTemplate, number_of_people: int = 1, for_resident: bool = False):
    price = room.price_for_resident if for_resident else room.price
    discount_from = room.price_for_resident_discount_from if for_resident else room.price_discount_from
    discount_until = room.price_for_resident_discount_until if for_resident else room.price_discount_until
    discount_unit = room.price_for_resident_discount_unit if for_resident else room.price_discount_unit
    discount_amount = room.price_for_resident_discount_amount if for_resident else room.price_discount_amount
    price_for_less_people_ = room.price_for_resident_less_people if for_resident else room.price_for_less_people

    if room.max_number_of_guests == number_of_people:
        final_price = _calculate_discount(price, discount_from, discount_until, discount_unit, discount_amount)
    else:
        final_price = None
        for price_for_less_people in price_for_less_people_ or []:
            if price_for_less_people['is_active'] and price_for_less_people['number_of_people'] == number_of_people:
                final_price = _calculate_discount(price, None, None, price_for_less_people['discount_unit'],
                                                  price_for_less_people['discount_amount'])
                break
    return final_price


async def create(user_id: int, booking_in: schemas.BookingCreate):
    db = get_db()
    try:
        booking = models.Booking(
            user_id=user_id,
            **booking_in.dict(exclude={"rooms"})
        )
        await booking.save(refresh=True)
        total_number_of_people, total_price = await create_booked_room(booking_id=booking.id, booking_in=booking_in)
        difference = booking.booked_to.date() - booking.booked_from.date()
        booking.total_price = total_price * int(difference.days)
        booking.total_number_of_people = total_number_of_people
        await db.commit()
        await db.refresh(booking)
        return booking
    except Exception as e:
        logger.error(e)
        await db.rollback()
        raise e


async def create_booked_room(booking_id: int, booking_in: schemas.BookingCreate):
    db = get_db()
    try:
        rooms: list[models.PropertyRoomTemplate] = await models.PropertyRoomTemplate.filter(
            {'id__in': [room.room_id for room in booking_in.rooms]}
        )
        rooms_map = {room.id: room for room in rooms}
        total_number_of_people, total_price = 0, 0

        for booked_room in booking_in.rooms:
            booked_room_id, number_of_people, price = (await db.execute(
                sa.insert(models.BookedRoom).values(dict(
                    booking_id=booking_id,
                    property_id=booking_in.property_id,
                    property_room_template_id=booked_room.room_id,
                    booked_from=booking_in.booked_from,
                    booked_to=booking_in.booked_to,
                    number_of_people=booked_room.number_of_people,
                    for_resident=booked_room.for_resident,
                    price=calculate_price(
                        rooms_map[booked_room.room_id],
                        number_of_people=booked_room.number_of_people,
                        for_resident=booked_room.for_resident,
                    )
                )).returning(
                    models.BookedRoom.id,
                    models.BookedRoom.number_of_people,
                    models.BookedRoom.price
                )
            )).fetchone()
            total_number_of_people += number_of_people
            total_price += price

            await models.BookedRoomBed(
                booked_room_id=booked_room_id,
                bed_type_id=booked_room.bed_type_id,
                bed_for_children=booked_room.bed_for_children,
            ).save()
        return total_number_of_people, total_price
    except Exception as e:
        logger.error(e)
        await db.rollback()
        raise e


async def update_booking(
        booking_id: int,
        booking_in: schemas.BookingUpdate,
        user_id: int
) -> schemas.Booking | None:
    db = get_db()
    try:
        booking = await models.Booking.get({'id': booking_id, 'user_id': user_id})
        if booking and booking.status == enums.BookingStatus.PENDING:
            booking.name = booking_in.name
            booking.booked_from = booking_in.booked_from
            booking.booked_to = booking_in.booked_to
            difference = booking.booked_to.date() - booking.booked_from.date()

            await db.execute(
                sa.delete(models.BookedRoom).where(models.BookedRoom.booking_id == booking_id)
            )
            total_number_of_people, total_price = await create_booked_room(
                booking_id=booking.id,
                booking_in=schemas.BookingCreate(
                    property_id=booking.property_id,
                    **booking_in.dict())
            )
            booking.total_number_of_people = total_number_of_people
            booking.total_price = total_price * int(difference.days)
            await db.commit()
            await db.refresh(booking)
            return booking
        elif booking.status == enums.BookingStatus.CONFIRMED:
            property_room_ids = [room.property_room_id for room in booking.rooms]
            booked_room_ids = [room.id for room in booking.rooms]

            property_rooms = (await db.execute(sa.select(models.PropertyRoom).where(
                operators.in_op(models.PropertyRoom.id, property_room_ids)
            ))).scalars().unique().all()
            property_rooms = {room.id: room for room in property_rooms}

            booking.name = booking_in.name
            booking.booked_from = booking_in.booked_from
            booking.booked_to = booking_in.booked_to
            difference = booking.booked_to.date() - booking.booked_from.date()

            for property_room in property_rooms.values():
                property_room.status = enums.RoomStatus.EMPTY

            await db.execute(sa.delete(models.PropertyRoomStatus).where(
                operators.in_op(
                    models.PropertyRoomStatus.booked_room_id, booked_room_ids
                )
            ))
            await db.execute(
                sa.delete(models.BookedRoom).where(models.BookedRoom.booking_id == booking_id)
            )

            total_number_of_people, total_price = await create_booked_room(
                booking_id=booking.id,
                booking_in=schemas.BookingCreate(
                    property_id=booking.property_id,
                    **booking_in.dict(),
                )
            )
            booking.total_price = total_price * int(difference.days)
            booking.total_number_of_people = total_number_of_people
            await db.commit()
            await db.refresh(booking)
            return booking
        return None
    except Exception as e:
        logger.error(e)
        await db.rollback()
        raise e


async def delete_booking(booking_id: int, user_id: int, reason_of_cancellation: str) -> bool:
    db = get_db()
    try:
        booking = await models.Booking.get({'id': booking_id, 'user_id': user_id})
        if booking and booking.status == enums.BookingStatus.PENDING:
            booking.status = enums.BookingStatus.CANCELED
            booking.canceled_by = enums.BookingCanceledBy.CLIENT
            booking.reason_of_cancellation = reason_of_cancellation
            rooms = []
            for room in booking.rooms:
                room.status = enums.BookingStatus.CANCELED
                room.cancellation_from_whom = enums.BookingCanceledBy.CLIENT
                room.reason_of_cancellation = reason_of_cancellation
                rooms.append(room)
            if rooms:
                db.add_all(rooms)
                await db.commit()
                return True
        elif booking and booking.status == enums.BookingStatus.CONFIRMED:
            property_room_ids = [room.property_room_id for room in booking.rooms]
            booked_room_ids = [room.id for room in booking.rooms]

            property_rooms = (await db.execute(sa.select(models.PropertyRoom).where(
                operators.in_op(models.PropertyRoom.id, property_room_ids)
            ))).scalars().unique().all()
            property_rooms = {room.id: room for room in property_rooms}

            await db.execute(sa.delete(models.PropertyRoomStatus).where(
                operators.in_op(models.PropertyRoomStatus.booked_room_id, booked_room_ids)
            ))

            dashboard_ = (await db.execute(sa.select(models.MerchantDashboard).join(
                models.Property, models.Property.added_by_id == models.MerchantDashboard.id
            ).where(
                models.Property.id == booking.property_id
            ))).scalar_one_or_none()

            booking.status = enums.BookingStatus.CANCELED
            booking.canceled_by = enums.BookingCanceledBy.CLIENT
            booking.reason_of_cancellation = reason_of_cancellation

            for room in booking.rooms:
                property_room = property_rooms[room.property_room_id]
                property_room.status = enums.RoomStatus.EMPTY
                with_draw, type_id = await with_draw_amount(room)
                dashboard_.balance += with_draw
                transaction = await models.Transaction(
                    title=enums.TransactionTitle.FOR_SERVICE,
                    status=enums.TransactionStatus.ERROR,
                    amount=with_draw,
                    order_id=booking.id,
                    balance=dashboard_.balance,
                    dashboard_id=dashboard_.id,
                    property_id=booking.property_id,
                    room_type_id=type_id,
                )
                db.add(transaction)
            await db.commit()
            return True
        else:
            return False
    except SQLAlchemyError as e:
        logger.error(e)
        await db.rollback()
        raise e


async def cancel_order(
        booking_id: int,
        property_id: int,
        reason_of_cancellation: str,
        is_arrived: bool = False,
        is_cancel: bool = False
):
    db = get_db()
    try:
        booking = await get_booking_(booking_id=booking_id, property_id=property_id)

        dashboard_ = (await db.execute(sa.select(models.MerchantDashboard).join(
            models.Property, models.Property.added_by_id == models.MerchantDashboard.id
        ).where(
            models.Property.id == property_id
        ))).scalar_one_or_none()

        if booking.status == enums.BookingStatus.CONFIRMED and dashboard_:
            property_room_ids = [room.property_room_id for room in booking.rooms]
            booked_room_ids = [room.id for room in booking.rooms]

            property_rooms = (await db.execute(sa.select(models.PropertyRoom).where(
                operators.in_op(models.PropertyRoom.id, property_room_ids)
            ))).scalars().unique().all()
            property_rooms = {room.id: room for room in property_rooms}

            await db.execute(sa.delete(models.PropertyRoomStatus).where(
                operators.in_op(
                    models.PropertyRoomStatus.booked_room_id,
                    booked_room_ids
                )
            ))
            booking.is_arrived = is_arrived
            booking.status = enums.BookingStatus.CANCELED
            booking.canceled_by = enums.BookingCanceledBy.MERCHANT_USER
            booking.reason_of_cancellation = reason_of_cancellation
            for room in booking.rooms:
                with_draw, room_type_id = await with_draw_amount(room)
                room.status = enums.BookingStatus.CANCELED
                property_room = property_rooms[room.property_room_id]
                property_room.status = enums.RoomStatus.EMPTY
                dashboard_.balance += with_draw
                transaction = models.Transaction(
                    title=enums.TransactionTitle.FOR_SERVICE,
                    status=enums.TransactionStatus.ERROR,
                    amount=with_draw,
                    order_id=booking.id,
                    balance=dashboard_.balance,
                    dashboard_id=dashboard_.id,
                    property_id=booking.property_id,
                    room_type_id=room_type_id,
                )
                db.add(transaction)
            await db.commit()
            await db.refresh(booking)
            return booking.user, True
        return None, False
    except Exception as e:
        logger.error(e)
        await db.rollback()
        raise e


async def change_order_status(status: enums.BookingStatus, booking_id: int, property_id: int):
    db = get_db()
    try:
        booking = await get_booking_(booking_id, property_id)
        if booking.status == enums.BookingStatus.CONFIRMED and status == enums.BookingStatus.ACTIVE:

            booking.status = enums.BookingStatus.ACTIVE
            db.add(booking)
            result = []
            for room in booking.rooms:
                room.status = enums.BookingStatus.ACTIVE
                result.append(room)
            if result:
                db.add_all(result)
                await db.commit()
                await db.refresh(booking)
                return True
        elif booking.status == enums.BookingStatus.ACTIVE and status == enums.BookingStatus.CLOSED:
            property_room_ids_ = [room.property_room_id for room in booking.rooms]
            property_rooms = (await db.execute(sa.select(models.PropertyRoom).where(
                operators.in_op(models.PropertyRoom.id, property_room_ids_)
            ))).scalars().unique().all()
            property_rooms = {room.id: room for room in property_rooms}

            booking.status = enums.BookingStatus.CLOSED
            result = []
            for room in booking.rooms:
                property_room = property_rooms[room.property_room_id]
                property_room.status = enums.RoomStatus.EMPTY
                result.append(property_room)
                room.status = enums.BookingStatus.CLOSED
                result.append(room)
            if result:
                db.add_all(result)
                await db.commit()
                await db.refresh(booking)
                return True
        return False
    except Exception as e:
        logger.error(e)
        await db.rollback()
        raise e


async def with_draw_amount(room: models.BookedRoom):
    db = get_db()
    price = room.price
    room_type_id = room.room.type_id

    with_draw_obj: models.WithdrawalAmount = (
        await db.execute(sa.select(models.WithdrawalAmount).where(
            models.WithdrawalAmount.room_type_id == room_type_id))
    ).scalar_one_or_none()

    if with_draw_obj:
        if room.for_resident:
            amount_unit = with_draw_obj.amount_unit_for_resident
            amount = (
                with_draw_obj.amount_for_resident if amount_unit == enums.BillingUnit.FIXED_VALUE
                else price * with_draw_obj.amount_for_resident / 100
            )
        else:
            amount_unit = with_draw_obj.amount_unit
            amount = (
                with_draw_obj.amount if amount_unit == enums.BillingUnit.FIXED_VALUE
                else price * with_draw_obj.amount / 100
            )
    else:
        amount = 1000

    return amount, room_type_id


async def accept_or_cancel_order(
        property_id: int,
        added_by_id: int,
        booking_id: int,
        obj_in: list[schemas.AcceptOrderWithRoom],
        accept_or_cancel: enums.AcceptOrCancel
):
    db = get_db()
    try:
        room_ids = {room.booked_room_id: room.room_id for room in obj_in}
        property_rooms = (
            await db.execute(sa.select(models.PropertyRoom).where(
                operators.in_op(models.PropertyRoom.id, [x.room_id for x in obj_in])))
        ).scalars().unique().all()

        property_rooms = {room.id: room for room in property_rooms}

        booking: schemas.Booking = await get_booking_(property_id=property_id, booking_id=booking_id)
        if booking:
            if accept_or_cancel == enums.AcceptOrCancel.ACCEPT:
                dashboard_: models.MerchantDashboard = (await db.execute(
                    sa.select(models.MerchantDashboard).where(models.MerchantDashboard.id == added_by_id)
                )).scalar_one_or_none()

                booking.status = enums.BookingStatus.CONFIRMED
                db.add(booking)
                total_with_draw_amount = sum(
                    with_draw for with_draw, _ in
                    [await with_draw_amount(room) for room in booking.rooms]
                )
                if dashboard_.balance >= total_with_draw_amount > 0:
                    for room, (with_draw, type_id) in zip(
                            booking.rooms,
                            [await with_draw_amount(room) for room in booking.rooms]
                    ):
                        if dashboard_.balance >= with_draw > 0:
                            room.property_room_id = room_ids[room.id]
                            property_room = property_rooms[room.property_room_id]
                            property_room.status = enums.RoomStatus.BUSY
                            db.add(property_room)
                            room.status = enums.BookingStatus.CONFIRMED
                            db.add(room)
                            dashboard_.balance -= with_draw
                            db.add(dashboard_)
                            room_status = models.PropertyRoomStatus(
                                property_room_id=room.property_room_id,
                                booked_room_id=room.id,
                                status=enums.RoomStatus.BUSY,
                                status_from=booking.booked_from.date(),
                                status_until=booking.booked_to.date()
                            )
                            db.add(room_status)
                            transaction = models.Transaction(
                                title=enums.TransactionTitle.FOR_SERVICE,
                                status=enums.TransactionStatus.SUCCESS,
                                amount=-with_draw,
                                order_id=booking.id,
                                balance=dashboard_.balance,
                                dashboard_id=added_by_id,
                                property_id=property_id,
                                room_type_id=type_id,
                            )
                            db.add(transaction)
                    await db.commit()
                    return True, 201, booking.user
                return True, 402, None
            else:
                booking.status = enums.BookingStatus.CANCELED
                booking.cancellation_from_whom = enums.BookingCanceledBy.MERCHANT_USER
                await db.commit()
                await db.refresh(booking)
                return False, 200, booking.user
    except Exception as e:
        logger.error(e)
        await db.rollback()
        raise e


def get_orders(
        property_id: int,
        sort_by: enums.OrderSortBy
):
    query = sa.select(models.Booking).where(
        models.Booking.property_id == property_id,
        models.Booking.status == enums.BookingStatus.PENDING
    )

    query = orders_sort_by_type(query, sort_by)

    return query


async def get_order(booking_id: int):
    db = get_db()
    query = sa.select(models.Booking).where(
        models.Booking.id == booking_id
    )
    return (await db.execute(query)).scalar_one_or_none()


async def get_empty_template_rooms(room_id: int, booked_from: date, booked_to: date, is_client: bool = False):
    db = get_db()
    rooms = (
        await db.execute(sa.select(models.PropertyRoom).where(
            models.PropertyRoom.room_id == room_id
        )
        )).scalars().unique().all()

    room_ids = (await db.execute(sa.select(models.PropertyRoomStatus.property_room_id).where(
        models.PropertyRoomStatus.status_from >= booked_from,
        models.PropertyRoomStatus.status_until <= booked_to,
        models.PropertyRoomStatus.status == enums.RoomStatus.BUSY,
    ))).scalars().unique().all()

    rooms = [r for r in rooms if r.id not in room_ids]
    if is_client:
        return len(rooms)
    return rooms


async def get_orders_statistics(property_id: int):
    db = get_db()
    query = sa.select(models.Booking).where(models.Booking.property_id == property_id)
    total_orders = (await db.execute(sa.select(sa.func.count()).select_from(query))).scalar()
    last_30_days = (await db.execute(sa.select(sa.func.count()).select_from(
        query.where(models.Booking.created_at >= datetime.now() - timedelta(days=30))))).scalar()
    yesterday = (await db.execute(sa.select(sa.func.count()).select_from(
        query.where(models.Booking.created_at >= datetime.now() - timedelta(days=1))))).scalar()
    today = (await db.execute(sa.select(sa.func.count()).select_from(
        query.where(sa.func.DATE(models.Booking.created_at) == datetime.now().date())))).scalar()

    return {
        'total_orders': total_orders,
        'last_30_days': last_30_days,
        'yesterday': yesterday,
        'today': today
    }


async def get_booking_statistics(days: enums.CountByDays, property_id: int):
    db = get_db()
    query = sa.select(models.Booking).where(models.Booking.property_id == property_id)
    if days.LAST_30_DAYS:
        query = query.where(models.Booking.created_at >= datetime.now() - timedelta(days=30))
    elif days.LAST_15_DAYS:
        query = query.where(models.Booking.created_at >= datetime.now() - timedelta(days=15))
    elif days.LAST_WEEK:
        query = query.where(models.Booking.created_at >= datetime.now() - timedelta(weeks=1))
    elif days.YESTERDAY:
        query = query.where(sa.func.DATE(models.Booking.created_at) == datetime.now().date() - timedelta(days=1))
    else:
        query = query.where(sa.func.DATE(models.Booking.created_at) == datetime.now().date())

    total_booking = (await db.execute(sa.select(sa.func.count()).select_from(query))).scalar()
    booked = (await db.execute(sa.select(func.count()).select_from(
        query.where(models.Booking.status == enums.BookingStatus.PENDING)))).scalar()
    reside = (await db.execute(
        sa.select(func.count()).select_from(query.where(models.Booking.status == enums.BookingStatus.ACTIVE)))).scalar()

    return {
        'total_booking': total_booking,
        'booked': booked,
        'reside': reside
    }


async def get_accounting(property_id: int, days: enums.CountByDays):
    db = get_db()
    query = sa.select(models.Booking).where(
        models.Booking.property_id == property_id).where(
        models.Booking.status == enums.BookingStatus.CLOSED
    )

    query_transaction = sa.select(models.Transaction).where(
        models.Transaction.property_id == property_id,
        models.Transaction.title == enums.TransactionTitle.FOR_SERVICE
    )

    if days.LAST_30_DAYS:
        query = query.where(models.Booking.created_at >= datetime.now() - timedelta(days=30))
        query_transaction = query_transaction.where(
            models.Transaction.created_at >= datetime.now() - timedelta(days=30)
        )
    elif days.LAST_15_DAYS:
        query = query.where(models.Booking.created_at >= datetime.now() - timedelta(days=15))
        query_transaction = query_transaction.where(
            models.Transaction.created_at >= datetime.now() - timedelta(days=15)
        )
    elif days.YESTERDAY:
        query = query.where(sa.func.DATE(models.Booking.created_at) == datetime.now().date() - timedelta(days=1))
        query_transaction = query_transaction.where(
            sa.func.DATE(models.Transaction.created_at) == datetime.now().date() - timedelta(days=1))
    else:
        query = query.where(sa.func.DATE(models.Booking.created_at) == datetime.now().date())
        query_transaction = query_transaction.where(
            sa.func.DATE(models.Transaction.created_at) == datetime.now().date())

    total = (await db.execute(sa.select(sa.func.sum(models.Booking.total_price)).select_from(query))).scalar() or 0
    withdraw = (await db.execute(
        sa.select(sa.func.sum(models.Transaction.amount)).select_from(query_transaction))).scalar() or 0

    return {
        'total': total,
        'withdraw': withdraw,
        'profit': total - withdraw
    }


def orders_sort_by_type(query, sort_by):
    sort_type_ = desc
    if sort_by.BY_DATE:
        query = query.order_by(sort_type_(models.Booking.created_at))
    elif sort_by.BY_ROOM:
        query.order_by(sort_type_(models.PropertyRoomTemplate.name))
    elif sort_by.BY_PRICE:
        query = query.order_by(sort_type_(models.Booking.total_price))
    elif sort_by.QTY_PEOPLE:
        query = query.order_by(sort_type_(models.Booking.total_number_of_people))
    return query


def merchant_booking_history(
        q: str,
        property_id: int,
        search_type: enums.SearchType,
        sort_by: enums.HistorySortBy,
        sort_type: enums.SortType,
        filter_by: enums.StatusBy,

):
    query = sa.select(models.Booking).where(
        models.Booking.property_id == property_id
    )
    if q:
        if search_type == enums.SearchType.ALL:
            if q.isnumeric():
                query = query.where(models.Booking.total_price == float(q))
            else:
                query = query.where(
                    operators.ilike_op(
                        models.Booking.name, f"%{q}%"
                    )
                )
        elif search_type.NAME:
            query = query.where(
                operators.ilike_op(
                    models.Booking.name, f"%{q}%"
                )
            )
        elif search_type.PRICE:
            query = query.where(
                models.Booking.total_price == float(q)
            )
    if filter_by:
        if filter_by == enums.StatusBy.ACTIVE:
            query = query.where(models.Booking.status == enums.BookingStatus.ACTIVE)
        else:
            query = query.where(models.Booking.status == enums.BookingStatus.CONFIRMED)

    query = query.where(
        models.Booking.status != enums.BookingStatus.PENDING,
        models.Booking.status != enums.BookingStatus.CLOSED,
        models.Booking.status != enums.BookingStatus.CANCELED,
    )

    query = filter_by_sort_type(query, sort_type, sort_by)

    return query


def order_history(
        q: str,
        search_type: enums.SearchType,
        sort_type: enums.SortType,
        sort_by: enums.HistorySortBy,
        filter_by: enums.OrderHistoryStatus,
        property_id: int,
):
    query = sa.select(models.Booking).where(
        models.Booking.property_id == property_id
    )
    if q:
        if search_type == enums.SearchType.ALL:
            if q.isnumeric():
                query = query.where(models.Booking.total_price == float(q))
            else:
                query = query.where(
                    operators.ilike_op(
                        models.Booking.name, f"%{q}%"
                    )
                )
        elif search_type.NAME:
            query = query.where(
                operators.ilike_op(
                    models.Booking.name, f"%{q}%"
                )
            )
        elif search_type.PRICE:
            query = query.where(
                models.Booking.total_price == float(q)
            )
    if filter_by:
        if filter_by == enums.OrderHistoryStatus.CLOSED:
            query = query.where(models.Booking.status == enums.BookingStatus.CLOSED)
        else:
            query = query.where(models.Booking.status == enums.BookingStatus.CANCELED)

    query = query.where(
        models.Booking.status != enums.BookingStatus.PENDING,
        models.Booking.status != enums.BookingStatus.CONFIRMED,
        models.Booking.status != enums.BookingStatus.ACTIVE
    )

    query = filter_by_sort_type(query, sort_type, sort_by)

    return query


def filter_by_sort_type(query, sort_type, sorty_by):
    sort_type_ = desc if sort_type == enums.SortType.DESC else asc
    query = query.order_by(desc(models.Booking.id))
    if sorty_by:
        if sorty_by == enums.HistorySortBy.ROOM_NAME:
            pass
        if sorty_by == enums.HistorySortBy.NAME:
            query = query.order_by(sort_type_(models.Booking.name))
        elif sorty_by == enums.HistorySortBy.CHECKIN_AND_CHECKOUT:
            query = query.order_by(sort_type_(models.Booking.booked_from))
        elif sorty_by == enums.HistorySortBy.NUMBER_OF_PEOPLE:
            query = query.order_by(sort_type_(models.Booking.total_number_of_people))
        elif sorty_by == enums.HistorySortBy.STATUS:
            query = query.order_by(sort_type_(models.Booking.status))
        elif sorty_by == enums.HistorySortBy.PRICE:
            query = query.order_by(sort_type_(models.Booking.total_price))
    return query
