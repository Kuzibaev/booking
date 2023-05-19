from sqladmin import ModelView

from app import models


class PropertyService(ModelView, model=models.PropertyService):
    column_list = [
        'id',
        'service_id',
        'property_id',
        'icon_id',
    ]


class PropertyType(ModelView, model=models.PropertyType):
    column_list = ['id', 'type']
    form_columns = [
        'type'
    ]


class PropertyTypeTranslation(ModelView, model=models.PropertyTypeTranslation):
    form_excluded_columns = [
        'id',
        'created_at',
        'updated_at'
    ]


class Property(ModelView, model=models.Property):
    form_columns = [
        "type",
        "city",
        "added_by",
        "name",
        "description",
        "address",
        "checkin_from",
        "checkin_until",
        "checkout_from",
        "checkout_until",
        "phone",
        "website",
        "is_active",
        "is_breakfast_served",
        "is_breakfast_included_in_price",
        "airport_distance",
        "railway_distance",
        "total_number_of_rooms",
        "minimum_price_per_night",
        "minimum_price_per_night_for_resident",
        "pets_allowed",
        "smoking_allowed",
        "latitude",
        "longitude",
        "city_centre_distance",
        "star_rating",
    ]
    column_list = [
        'id',
        *form_columns
    ]


class PropertyTranslation(ModelView, model=models.PropertyTranslation):
    column_list = [models.PropertyTranslation.id, models.PropertyTranslation.language]
    form_columns = [
        "property",
        "description",
        "address",
        "language",
        "is_default"
    ]


class PropertyPhoto(ModelView, model=models.PropertyPhoto):
    form_columns = [
        'photo',
        'property',
        'is_default',
    ]
    column_list = [
        'id',
        'property_id',
        'photo_id'
    ]


class RoomType(ModelView, model=models.RoomType):
    form_columns = ['type']
    column_list = ['id', 'type']


class RoomTypeTranslation(ModelView, model=models.RoomTypeTranslation):
    column_list = [models.RoomTypeTranslation.id, models.RoomTypeTranslation.language]
    form_columns = ['type', 'room_type', 'language']


class RoomName(ModelView, model=models.RoomName):
    form_columns = ['name', 'type']
    column_list = ['id', 'name', 'type']


class BedType(ModelView, model=models.BedType):
    form_columns = ['type']
    column_list = ['id', 'type']


class RoomBed(ModelView, model=models.RoomBed):
    form_columns = ['bed_type', 'number_of_beds']
    column_list = ['id', 'bed_type', 'number_of_beds']


class RoomPhoto(ModelView, model=models.RoomPhoto):
    form_columns = ['photo', 'room']
    column_list = ['id', 'photo']


class PropertyRoomTemplate(ModelView, model=models.PropertyRoomTemplate):
    form_columns = [
        "property",
        "type",
        "name",
        "number_of_rooms",
        "max_number_of_guests",
        "max_number_of_children",
        "area",
        "services",
    ]
    column_list = [
        'id',
        'property_id',
        'name'
    ]


class PropertyRoom(ModelView, model=models.PropertyRoom):
    form_columns = [
        'room',
        'name'
    ]
    column_list = [
        'id',
        'room_id',
        'name'
    ]
