from sqladmin import ModelView

from app import models


class Booking(ModelView, model=models.Booking):
    can_create = False
    can_export = False
    column_list = [
        'id',
        'name',
        'property',
        'user',
        'status',
        'booked_from',
        'booked_to',
        'total_price',
        'total_number_of_people',
        'reason_of_cancellation',
        'canceled_by'
    ]


class BookedRoom(ModelView, model=models.BookedRoom):
    can_create = False
    can_export = False

    column_list = ['id', 'booking_id', 'status', 'booked_from', 'booked_to', 'price']
