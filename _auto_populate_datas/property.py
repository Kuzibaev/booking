import datetime

from app import models
from app.models import enums
from app.models.enums import RoomStatus
from ._conf import DBRecord, ModelData, HOTELS

_service = DBRecord(models.Service)
_photo = DBRecord(models.DocFile)
_r_type = DBRecord(models.RoomType)
_r_name = DBRecord(models.RoomName)
_bed_type = DBRecord(models.BedType)

DATAS = [
    {
        "type_id": DBRecord(models.PropertyType, filters=[models.PropertyType.type == "Hotel"]),
        "name": 'Reikartz Amirun Hotel',
        "description": ("The Reikartz Amirun Hotel is located in the center of Tashkent, "
                        "a 5-minute drive from the Islam Karimov International Airport. "
                        "The hotel has 67 rooms of increased comfort: single, double, "
                        "deluxe, and suites. The hotel has a restaurant, summer terrace, "
                        "conference room, gym, swimming pool and hammam. Accommodation at "
                        "the hotel includes a delicious and delicious breakfast and impeccable "
                        "service from the hotel's professional team. You can always book the "
                        "desired room in advance."
                        "The hotel also provides additional services "
                        "for ordering a taxi, transfer to / from the airport and railway station."),
        "added_by_id": 1,
        "website": "example.com",
        "phone": "+998901234567",
        "address": "Tashkent, 150 A.Kahhara Str, Yakkasaray district",
        "latitude": 65.34234234,
        "longitude": 45.324234,
        "city_centre_distance": 4700,
        "city_id": DBRecord(models.City, filters=[models.City.name_slug == "tashkent"]),
        "star_rating": enums.PropertyStarRating.FIVE,
        "minimum_price_per_night": 490000,
        "minimum_price_per_night_for_resident": 350000,
        "checkin_from": datetime.datetime(2023, 1, 1, 14, 00, 00),
        "checkin_until": datetime.datetime(2023, 1, 1, 14, 00, 00),
        "checkout_from": datetime.datetime(2023, 1, 1, 14, 00, 00),
        "checkout_until": datetime.datetime(2023, 1, 1, 14, 00, 00),
        "is_active": enums.PropertyStatus.ACTIVE,
        "photos": ModelData(
            models.PropertyPhoto,
            [
                {"photo_id": _photo([models.DocFile.name == "demo_property_image_1.jpg"])},
                {"photo_id": _photo([models.DocFile.name == "demo_property_image_2.jpg"])},
                {"photo_id": _photo([models.DocFile.name == "demo_property_image_3.jpg"])},
                {"photo_id": _photo([models.DocFile.name == "demo_property_image_4.jpg"])},
                {"photo_id": _photo([models.DocFile.name == "demo_property_image_5.jpg"])},
            ],
            'property_id'
        ),
        "translations": ModelData(
            models.PropertyTranslation,
            [
                {
                    'language': enums.Languages.EN,
                    'description': ("The Reikartz Amirun Hotel is located in the center of Tashkent, "
                                    "a 5-minute drive from the Islam Karimov International Airport. "
                                    "The hotel has 67 rooms of increased comfort: single, double, "
                                    "deluxe, and suites. The hotel has a restaurant, summer terrace, "
                                    "conference room, gym, swimming pool and hammam. Accommodation at "
                                    "the hotel includes a delicious and delicious breakfast and impeccable "
                                    "service from the hotel's professional team. You can always book the "
                                    "desired room in advance."
                                    "The hotel also provides additional services "
                                    "for ordering a taxi, transfer to / from the airport and railway station."),
                    'address': "Tashkent, 150 A.Kahhara Str, Yakkasaray district"
                },
                {
                    'language': enums.Languages.UZ,
                    'description': ("Reikartz Amirun mehmonxonasi Toshkent markazida, "
                                    "Islom Karimov nomidagi xalqaro aeroportdan 5 daqiqalik "
                                    "masofada joylashgan. Mehmonxonada qulayligi yuqori bo'lgan "
                                    "67 ta xona mavjud: bir kishilik, ikki kishilik, delyuks va lyuks. "
                                    "Mehmonxonada restoran, yozgi terassa, konferents-zal, sport zali, "
                                    "basseyn va hamam mavjud. Mehmonxonada mazali nonushta va professional "
                                    "xodimlarning benuqson xizmatini o'z ichiga oladi. Siz har doim kerakli "
                                    "xonani oldindan bron qilishingiz mumkin."
                                    "Shuningdek mehmonxona taksiga buyurtma berish, aeroport va temir "
                                    "yo'l vokzaliga transfer xizmatlarini ko'rsatadi."),
                    'address': "Toshkent, Yakkasaroy tumani, A.Qahhor ko'chasi, 150 uy."
                },
                {
                    'language': enums.Languages.RU,
                    'description': ("Гостиница Reikartz Amirun находится в центре Ташкента в "
                                    "5 минутах езды от международного аэропорта имени Ислама Каримова. "
                                    "Номерной фонд гостиницы составляет 67 номеров повышенного "
                                    "комфорта: одноместные, двухместные, делюкс, и номера категории люкс. "
                                    "На территории отеля есть ресторан, летняя терраса, конференц-зал, "
                                    "тренажерный зал , бассейн и хаммам. Проживание в отеле включает в себя "
                                    "изысканный и вкусный завтрак и безупречный сервис от профессиональной "
                                    "команды сотрудников отеля. Вы всегда можете заранее забронировать желаемый номер."
                                    "Гостиница также предоставляет дополнительные услуги по заказу "
                                    "такси, трансфера в/из аэропорта и железнодорожного вокзала."),
                    'address': "Ташкент, Яккасарайский р-он, ул. А.Каххара 150"
                }
            ],
            "property_id"
        ),
        "services": ModelData(
            models.PropertyService,
            [
                {
                    "service_id": _service(
                        [models.Service.service_name == "Wi-fi",
                         models.ServiceCategory.category_name == "Popular services"]
                    ),
                    "icon_id": _photo([models.DocFile.name == "service_wi_fi.png"])

                },
                {
                    "service_id": _service(
                        [models.Service.service_name == "Garden",
                         models.ServiceCategory.category_name == "Popular services"]
                    ),
                    "icon_id": _photo([models.DocFile.name == "service_garden.png"])

                },
                {
                    "service_id": _service(
                        [models.Service.service_name == "Swimming Pool",
                         models.ServiceCategory.category_name == "Popular services"]
                    ),
                    "icon_id": _photo([models.DocFile.name == "service_swimming_pool.png"])

                },
                {
                    "service_id": _service(
                        [models.Service.service_name == "Sauna",
                         models.ServiceCategory.category_name == "Popular services"]
                    ),
                    "icon_id": _photo([models.DocFile.name == "service_sauna.png"])

                }
            ],
            'property_id'
        ),
        "rooms": ModelData(
            models.PropertyRoomTemplate,
            [
                {
                    "type_id": _r_type([models.RoomType.type == "Double room"]),
                    "name_id": _r_name(
                        [models.RoomName.name == "Deluxe Double Room", models.RoomType.type == "Double room"]
                    ),
                    "number_of_rooms": 4,
                    "max_number_of_guests": 5,
                    "max_number_of_children": 2,
                    "area": 56,
                    "price": 490000,
                    "price_has_discount": True,
                    "price_discount_unit": "fixed_value",
                    "price_discount_amount": 20000,
                    "price_for_resident": 400000,
                    "price_for_resident_has_discount": True,
                    "price_for_resident_discount_unit": "fixed_value",
                    "price_for_resident_discount_amount": 20000,
                    "price_for_less_people": [
                        {
                            "number_of_people": 4,
                            "discount_unit": "fixed_value",
                            "discount_amount": 50000,
                            "is_active": True
                        },
                        {
                            "number_of_people": 3,
                            "discount_unit": "fixed_value",
                            "discount_amount": 80000,
                            "is_active": True
                        }
                    ],
                    "price_for_resident_less_people": [
                        {
                            "number_of_people": 4,
                            "discount_unit": "fixed_value",
                            "discount_amount": 20000,
                            "is_active": True
                        },
                        {
                            "number_of_people": 3,
                            "discount_unit": "fixed_value",
                            "discount_amount": 80000,
                            "is_active": True
                        }
                    ],
                    "rooms": ModelData(
                        models.PropertyRoom,
                        [
                            {
                                "name": "A1",
                                "status": enums.RoomStatus.EMPTY,
                            },
                            {"name": "A2",
                             "status": enums.RoomStatus.EMPTY,
                             },
                            {"name": "A3",
                             "status": enums.RoomStatus.EMPTY,
                             },
                            {
                                "name": "A4",
                                "status": enums.RoomStatus.EMPTY,
                            },
                        ],
                        "room_id",

                    ),
                    "beds": ModelData(
                        models.RoomBed,
                        [
                            {"bed_type_id": _bed_type([models.BedType.type == "Single bed"])},
                            {"bed_type_id": _bed_type([models.BedType.type == "Double bed"])},
                        ],
                        "room_id"
                    ),
                    "photos": ModelData(
                        models.RoomPhoto,
                        [
                            {"photo_id": _photo([models.DocFile.name == "demo_property_image_6.jpg"])},
                            {"photo_id": _photo([models.DocFile.name == "demo_property_image_7.jpg"])},
                            {"photo_id": _photo([models.DocFile.name == "demo_property_image_8.jpg"])},
                            {"photo_id": _photo([models.DocFile.name == "demo_property_image_9.jpg"])},
                        ],
                        'room_id'
                    ),
                    "services": ModelData(
                        models.RoomService,
                        [
                            {"service_id": _service([models.Service.service_name == "Shower",
                                                     models.ServiceCategory.category_name == "Bathroom"])},
                            {"service_id": _service([models.Service.service_name == "Iron",
                                                     models.ServiceCategory.category_name == "Facilities"])},
                            {"service_id": _service([models.Service.service_name == "Pajamas",
                                                     models.ServiceCategory.category_name == "Facilities"])},
                            {"service_id": _service([models.Service.service_name == "Towels",
                                                     models.ServiceCategory.category_name == "Bathroom"])},
                            {"service_id": _service([models.Service.service_name == "Toothbrush",
                                                     models.ServiceCategory.category_name == "Bathroom"])},
                        ],
                        'room_id'
                    ),
                },
                {
                    "type_id": _r_type([models.RoomType.type == "Double room"]),
                    "name_id": _r_name(
                        [models.RoomName.name == "Double Room with park view", models.RoomType.type == "Double room"]),
                    "number_of_rooms": 10,
                    "max_number_of_guests": 2,
                    "max_number_of_children": 2,
                    "area": 51,
                    "price": 450000,
                    "price_has_discount": True,
                    "price_discount_unit": "fixed_value",
                    "price_discount_amount": 20000,
                    "price_for_resident": 350000,
                    "price_for_resident_has_discount": True,
                    "price_for_resident_discount_unit": "fixed_value",
                    "price_for_resident_discount_amount": 20000,
                    "price_for_less_people": [
                        {
                            "number_of_people": 1,
                            "discount_unit": "fixed_value",
                            "discount_amount": 50000,
                            "is_active": True
                        }
                    ],
                    "price_for_resident_less_people": [
                        {
                            "number_of_people": 1,
                            "discount_unit": "fixed_value",
                            "discount_amount": 30000,
                            "is_active": True
                        }
                    ],
                    "rooms": ModelData(
                        models.PropertyRoom,
                        [
                            {"name": "B1",
                             "status": enums.RoomStatus.EMPTY
                             },
                            {"name": "B2",
                             "status": enums.RoomStatus.EMPTY
                             },
                            {
                                "name": "B3",
                                "status": enums.RoomStatus.EMPTY,
                            },
                            {
                                "name": "B4",
                                "status": enums.RoomStatus.EMPTY,
                            },
                            {
                                "name": "B5",
                                "status": enums.RoomStatus.EMPTY,
                            },
                            {
                                "name": "B7",
                                "status": enums.RoomStatus.EMPTY,
                            },
                            {
                                "name": "B8",
                                "status": enums.RoomStatus.EMPTY,
                            },
                            {
                                "name": "B9",
                                "status": enums.RoomStatus.EMPTY,
                            },
                            {
                                "name": "B10",
                                "status": enums.RoomStatus.EMPTY,
                            },
                        ],
                        "room_id"
                    ),
                    "beds": ModelData(
                        models.RoomBed,
                        [
                            {"bed_type_id": _bed_type([models.BedType.type == "Single bed"])},
                            {"bed_type_id": _bed_type([models.BedType.type == "Double bed"])},
                        ],
                        "room_id"
                    ),
                    "photos": ModelData(
                        models.RoomPhoto,
                        [
                            {"photo_id": _photo([models.DocFile.name == "demo_property_image_1.jpg"])},
                            {"photo_id": _photo([models.DocFile.name == "demo_property_image_2.jpg"])},
                            {"photo_id": _photo([models.DocFile.name == "demo_property_image_3.jpg"])},
                            {"photo_id": _photo([models.DocFile.name == "demo_property_image_4.jpg"])},
                        ],
                        'room_id'
                    ),
                    "services": ModelData(
                        models.RoomService,
                        [
                            {"service_id": _service([models.Service.service_name == "Toothbrush",
                                                     models.ServiceCategory.category_name == "Bathroom"])},
                            {"service_id": _service([models.Service.service_name == "Iron",
                                                     models.ServiceCategory.category_name == "Facilities"])},
                            {"service_id": _service([models.Service.service_name == "Pajamas",
                                                     models.ServiceCategory.category_name == "Facilities"])},
                            {"service_id": _service([models.Service.service_name == "Towels",
                                                     models.ServiceCategory.category_name == "Bathroom"])},
                            {"service_id": _service([models.Service.service_name == "Shower",
                                                     models.ServiceCategory.category_name == "Bathroom"])},
                        ],
                        'room_id'
                    ),
                }
            ],
            'property_id'
        )
    },
    {
        "type_id": DBRecord(models.PropertyType, filters=[models.PropertyType.type == "Hotel"]),
        "name": 'Huzur Hotel',
        "description": ("Located in Tashkent, Huzur Hotel Tashkent provides a bar and shared lounge. "
                        "Among the facilities of this property are a restaurant, a 24-hour "
                        "front desk and room service, along with free WiFi throughout the property. "
                        "There is free private parking and the property "
                        "features paid airport shuttle service."
                        "All units are equipped with air conditioning, "
                        "a flat-screen TV with satellite channels, a fridge, a kettle, "
                        "a shower, bathrobes and a desk. All rooms include "
                        "a private bathroom, slippers and bed linen."),
        "added_by_id": 1,
        "website": "example.com",
        "phone": "+998901234567",
        "address": "Tashkent, 150 A.Kahhara Str, Yakkasaray district",
        "latitude": 65.34234234,
        "longitude": 45.324234,
        "city_centre_distance": 6700,
        "city_id": DBRecord(models.City, filters=[models.City.name_slug == "tashkent"]),
        "star_rating": enums.PropertyStarRating.FIVE,
        "minimum_price_per_night": 350000,
        "minimum_price_per_night_for_resident": 300000,
        "checkin_from": datetime.datetime(2023, 1, 1, 14, 00, 00),
        "checkin_until": datetime.datetime(2023, 1, 1, 14, 00, 00),
        "checkout_from": datetime.datetime(2023, 1, 1, 14, 00, 00),
        "checkout_until": datetime.datetime(2023, 1, 1, 14, 00, 00),
        "is_active": enums.PropertyStatus.ACTIVE,
        "photos": ModelData(
            models.PropertyPhoto,
            [
                {"photo_id": _photo([models.DocFile.name == "demo_property_image_21.jpg"])},
                {"photo_id": _photo([models.DocFile.name == "demo_property_image_22.jpg"])},
                {"photo_id": _photo([models.DocFile.name == "demo_property_image_23.jpg"])},
                {"photo_id": _photo([models.DocFile.name == "demo_property_image_24.jpg"])},
                {"photo_id": _photo([models.DocFile.name == "demo_property_image_25.jpg"])},
            ],
            'property_id'
        ),
        "translations": ModelData(
            models.PropertyTranslation,
            [
                {
                    'language': enums.Languages.EN,
                    'description': ("Located in Tashkent, Huzur Hotel Tashkent provides a bar and shared lounge. "
                                    "Among the facilities of this property are a restaurant, a 24-hour "
                                    "front desk and room service, along with free WiFi throughout the property. "
                                    "There is free private parking and the property "
                                    "features paid airport shuttle service."
                                    "All units are equipped with air conditioning, "
                                    "a flat-screen TV with satellite channels, a fridge, a kettle, "
                                    "a shower, bathrobes and a desk. All rooms include "
                                    "a private bathroom, slippers and bed linen."),
                    'address': "Tashkent, 39a,Mayqurgon,Yunusabad district."
                },
                {
                    'language': enums.Languages.UZ,
                    'description': ("Huzur mehmonxonasi Toshkent shahrida joylashgan. "
                                    "Bu yerda bar, restoran, 24 soatlik qabulxona va barcha "
                                    "hududlarda bepul Wi-Fi mavjud. Xona xizmati ko'rsatiladi. "
                                    "Memonxona hududida bepul shaxsiy avtoturargoh mavjud. "
                                    "Qo'shimcha to'lov evaziga aeroportga transport xizmati ko'rsatilishi mumkin."
                                    "Har bir xonada ish stoli va dush, xalat bilan "
                                    "jihozlangan shaxsiy hammom mavjud. "
                                    "Standart qulayliklar orasida konditsioner, muzlatgich, "
                                    "choynak va sun'iy yo'ldosh kanallari bilan tekis ekranli "
                                    "televizor mavjud. Choyshab beriladi."),
                    'address': "Toshkent, Yunusobod tumani,Mayqurgon ko'chasi,39a-uy."
                },
                {
                    'language': enums.Languages.RU,
                    'description': ("Отель Huzur расположен в Ташкенте. К услугам гостей бар, "
                                    "ресторан, круглосуточная стойка регистрации и бесплатный "
                                    "Wi-Fi во всех зонах. Осуществляется доставка еды и напитков в номер. "
                                    "На территории обустроена бесплатная частная парковка. "
                                    "За дополнительную плату для гостей организуют трансфер от/до аэропорта."
                                    "В каждом номере есть письменный стол и собственная "
                                    "ванная комната с душем, халатами и тапочками. "
                                    "В числе стандартных удобств — кондиционер, холодильник, "
                                    "чайник и телевизор с плоским экраном и спутниковыми каналами. "
                                    "Предоставляется постельное белье."),
                    'address': "Ташкент, Юнусабадский р-он,ул.Майкурган,д.39а."
                }
            ],
            "property_id"
        ),
        "services": ModelData(
            models.PropertyService,
            [
                {
                    "service_id": _service(
                        [models.Service.service_name == "Wi-fi",
                         models.ServiceCategory.category_name == "Popular services"]
                    ),
                    "icon_id": _photo([models.DocFile.name == "service_wi_fi.png"])

                },
                {
                    "service_id": _service(
                        [models.Service.service_name == "Garden",
                         models.ServiceCategory.category_name == "Popular services"]
                    ),
                    "icon_id": _photo([models.DocFile.name == "service_garden.png"])

                },
                {
                    "service_id": _service(
                        [models.Service.service_name == "Swimming Pool",
                         models.ServiceCategory.category_name == "Popular services"]
                    ),
                    "icon_id": _photo([models.DocFile.name == "service_swimming_pool.png"])

                },
                {
                    "service_id": _service(
                        [models.Service.service_name == "Sauna",
                         models.ServiceCategory.category_name == "Popular services"]
                    ),
                    "icon_id": _photo([models.DocFile.name == "service_sauna.png"])

                },

            ],
            'property_id'
        ),
        "rooms": ModelData(
            models.PropertyRoomTemplate,
            [
                {
                    "type_id": _r_type([models.RoomType.type == "Double room"]),
                    "name_id": _r_name(
                        [models.RoomName.name == "Deluxe Double Room", models.RoomType.type == "Double room"]
                    ),
                    "number_of_rooms": 4,
                    "max_number_of_guests": 2,
                    "max_number_of_children": 2,
                    "area": 56,
                    "pets_allowed": True,
                    "smoking_allowed": False,
                    "price": 300000,
                    "price_for_resident": 350000,
                    "rooms": ModelData(
                        models.PropertyRoom,
                        [
                            {
                                "name": "A1",
                                "status": enums.RoomStatus.EMPTY,
                            },
                            {
                                "name": "A2",
                                "status": enums.RoomStatus.EMPTY,
                            },
                            {
                                "name": "A3",
                                "status": enums.RoomStatus.EMPTY,
                            },
                            {
                                "name": "A4",
                                "status": enums.RoomStatus.EMPTY,
                            },

                        ],
                        "room_id"
                    ),
                    "beds": ModelData(
                        models.RoomBed,
                        [
                            {"bed_type_id": _bed_type([models.BedType.type == "Single bed"])},
                            {"bed_type_id": _bed_type([models.BedType.type == "Double bed"])},
                        ],
                        "room_id"
                    ),
                    "photos": ModelData(
                        models.RoomPhoto,
                        [
                            {"photo_id": _photo([models.DocFile.name == "demo_property_image_26.jpg"])},
                            {"photo_id": _photo([models.DocFile.name == "demo_property_image_27.jpg"])},
                            {"photo_id": _photo([models.DocFile.name == "demo_property_image_28.jpg"])},
                            {"photo_id": _photo([models.DocFile.name == "demo_property_image_29.jpg"])},
                        ],
                        'room_id'
                    ),
                    "services": ModelData(
                        models.RoomService,
                        [
                            {"service_id": _service([models.Service.service_name == "Shower",
                                                     models.ServiceCategory.category_name == "Bathroom"])},
                            {"service_id": _service([models.Service.service_name == "Iron",
                                                     models.ServiceCategory.category_name == "Facilities"])},
                            {"service_id": _service([models.Service.service_name == "Pajamas",
                                                     models.ServiceCategory.category_name == "Facilities"])},
                            {"service_id": _service([models.Service.service_name == "Towels",
                                                     models.ServiceCategory.category_name == "Bathroom"])},
                            {"service_id": _service([models.Service.service_name == "Toothbrush",
                                                     models.ServiceCategory.category_name == "Bathroom"])},
                        ],
                        'room_id'
                    ),
                },
                {
                    "type_id": _r_type([models.RoomType.type == "Double room"]),
                    "name_id": _r_name(
                        [models.RoomName.name == "Double Room with park view", models.RoomType.type == "Double room"]),
                    "number_of_rooms": 10,
                    "max_number_of_guests": 2,
                    "max_number_of_children": 4,
                    "area": 51,
                    "pets_allowed": True,
                    "smoking_allowed": True,
                    "price": 5000000,
                    "price_for_resident": 400000,
                    "rooms": ModelData(
                        models.PropertyRoom,
                        [
                            {
                                "name": "B1",
                                "status": enums.RoomStatus.EMPTY,
                            },
                            {
                                "name": "B2",
                                "status": enums.RoomStatus.EMPTY,
                            },
                            {
                                "name": "B3",
                                "status": enums.RoomStatus.EMPTY,
                            },
                            {
                                "name": "B4",
                                "status": enums.RoomStatus.EMPTY,

                            },

                        ],
                        "room_id"
                    ),
                    "beds": ModelData(
                        models.RoomBed,
                        [
                            {"bed_type_id": _bed_type([models.BedType.type == "Single bed"])},
                            {"bed_type_id": _bed_type([models.BedType.type == "Double bed"])},
                        ],
                        "room_id"
                    ),
                    "photos": ModelData(
                        models.RoomPhoto,
                        [
                            {"photo_id": _photo([models.DocFile.name == "demo_property_image_21.jpg"])},
                            {"photo_id": _photo([models.DocFile.name == "demo_property_image_22.jpg"])},
                            {"photo_id": _photo([models.DocFile.name == "demo_property_image_23.jpg"])},
                            {"photo_id": _photo([models.DocFile.name == "demo_property_image_24.jpg"])},
                        ],
                        'room_id'
                    ),
                    "services": ModelData(
                        models.RoomService,
                        [
                            {"service_id": _service([models.Service.service_name == "Toothbrush",
                                                     models.ServiceCategory.category_name == "Bathroom"])},
                            {"service_id": _service([models.Service.service_name == "Iron",
                                                     models.ServiceCategory.category_name == "Facilities"])},
                            {"service_id": _service([models.Service.service_name == "Pajamas",
                                                     models.ServiceCategory.category_name == "Facilities"])},
                            {"service_id": _service([models.Service.service_name == "Towels",
                                                     models.ServiceCategory.category_name == "Bathroom"])},
                            {"service_id": _service([models.Service.service_name == "Shower",
                                                     models.ServiceCategory.category_name == "Bathroom"])},
                        ],
                        'room_id'
                    ),
                }
            ],
            'property_id'
        )
    },
]
for hotel in HOTELS:
    property_data = {
        'type_id': DBRecord(models.PropertyType, filters=[models.PropertyType.type == "Hotel"]),
        'name': hotel['title'],
        'description': hotel['description'],
        "added_by_id": 1,
        "website": "example.com",
        "phone": "+998901234567",
        "address": hotel['address'],
        "latitude": float(hotel['latitude']),
        "longitude": float(hotel['longitude']),
        "city_centre_distance": float(hotel['city_centre_distance']) * 1000,
        "city_id": DBRecord(models.City, filters=[models.City.name_slug == hotel['city']]),
        "star_rating": enums.PropertyStarRating.FIVE,
        "minimum_price_per_night": 450000,
        "minimum_price_per_night_for_resident": 350000,
        "checkin_from": datetime.datetime(2023, 1, 1, 14, 00, 00),
        "checkin_until": datetime.datetime(2023, 1, 1, 14, 00, 00),
        "checkout_from": datetime.datetime(2023, 1, 1, 14, 00, 00),
        "checkout_until": datetime.datetime(2023, 1, 1, 14, 00, 00),
        "is_active": enums.PropertyStatus.ACTIVE,
        "photos": ModelData(
            models.PropertyPhoto,
            [
                {"photo_id": _photo(
                    [models.DocFile.name == f"{hotel['slug']}_{photo_num}.{photo.rsplit('.', maxsplit=1)[1]}"]
                )}
                for photo_num, photo in enumerate(hotel['photos'])
            ],
            'property_id'
        ),
        "translations": ModelData(
            models.PropertyTranslation,
            [
                {
                    'language': enums.Languages.EN,
                    'description': hotel['description'],
                    'address': hotel['address']
                },
                {
                    'language': enums.Languages.UZ,
                    'description': hotel['translations'][0]['description'],
                    'address': hotel['translations'][0]['address']
                },
                {
                    'language': enums.Languages.RU,
                    'description': hotel['translations'][1]['description'],
                    'address': hotel['translations'][1]['address']
                },

            ],
            'property_id'
        ),
        "services": ModelData(
            models.PropertyService,
            [
                {
                    "service_id": _service(
                        [models.Service.service_name == "Wi-fi",
                         models.ServiceCategory.category_name == "Popular services"]
                    ),
                    "icon_id": _photo([models.DocFile.name == "service_wi_fi.png"])

                },
                {
                    "service_id": _service(
                        [models.Service.service_name == "Garden",
                         models.ServiceCategory.category_name == "Popular services"]
                    ),
                    "icon_id": _photo([models.DocFile.name == "service_garden.png"])

                },
                {
                    "service_id": _service(
                        [models.Service.service_name == "Swimming Pool",
                         models.ServiceCategory.category_name == "Popular services"]
                    ),
                    "icon_id": _photo([models.DocFile.name == "service_swimming_pool.png"])

                },
                {
                    "service_id": _service(
                        [models.Service.service_name == "Sauna",
                         models.ServiceCategory.category_name == "Popular services"]
                    ),
                    "icon_id": _photo([models.DocFile.name == "service_sauna.png"])

                },

            ],
            'property_id'
        ),
        "rooms": ModelData(
            models.PropertyRoomTemplate,
            [
                {
                    "type_id": _r_type([models.RoomType.type == "Double room"]),
                    "name_id": _r_name(
                        [models.RoomName.name == "Deluxe Double Room", models.RoomType.type == "Double room"]
                    ),
                    "number_of_rooms": 4,
                    "max_number_of_guests": 2,
                    "max_number_of_children": 2,
                    "area": 56,
                    "pets_allowed": False,
                    "smoking_allowed": True,
                    "price": 450000,
                    "price_for_resident": 350000,
                    "rooms": ModelData(
                        models.PropertyRoom,
                        [
                            {
                                "name": "A1",
                                "status": enums.RoomStatus.EMPTY,
                            },
                            {
                                "name": "A2",
                                "status": enums.RoomStatus.EMPTY,
                            },
                            {
                                "name": "A3",
                                "status": enums.RoomStatus.EMPTY,
                            },
                            {
                                "name": "A4",
                                "status": enums.RoomStatus.EMPTY
                            },

                        ],
                        "room_id"
                    ),
                    "beds": ModelData(
                        models.RoomBed,
                        [
                            {"bed_type_id": _bed_type([models.BedType.type == "Single bed"])},
                            {"bed_type_id": _bed_type([models.BedType.type == "Double bed"])},
                        ],
                        "room_id"
                    ),
                    "photos": ModelData(
                        models.RoomPhoto,
                        [
                            {"photo_id": _photo([models.DocFile.name == "demo_property_image_26.jpg"])},
                            {"photo_id": _photo([models.DocFile.name == "demo_property_image_27.jpg"])},
                            {"photo_id": _photo([models.DocFile.name == "demo_property_image_28.jpg"])},
                            {"photo_id": _photo([models.DocFile.name == "demo_property_image_29.jpg"])},
                        ],
                        'room_id'
                    ),
                    "services": ModelData(
                        models.RoomService,
                        [
                            {"service_id": _service([models.Service.service_name == "Shower",
                                                     models.ServiceCategory.category_name == "Bathroom"])},
                            {"service_id": _service([models.Service.service_name == "Iron",
                                                     models.ServiceCategory.category_name == "Facilities"])},
                            {"service_id": _service([models.Service.service_name == "Pajamas",
                                                     models.ServiceCategory.category_name == "Facilities"])},
                            {"service_id": _service([models.Service.service_name == "Towels",
                                                     models.ServiceCategory.category_name == "Bathroom"])},
                            {"service_id": _service([models.Service.service_name == "Toothbrush",
                                                     models.ServiceCategory.category_name == "Bathroom"])},
                        ],
                        'room_id'
                    ),
                },
                {
                    "type_id": _r_type([models.RoomType.type == "Double room"]),
                    "name_id": _r_name(
                        [models.RoomName.name == "Double Room with park view", models.RoomType.type == "Double room"]),
                    "number_of_rooms": 4,
                    "max_number_of_guests": 2,
                    "max_number_of_children": 4,
                    "area": 51,
                    "price": 450000,
                    "price_for_resident": 350000,
                    "rooms": ModelData(
                        models.PropertyRoom,
                        [
                            {
                                "name": "B1",
                                "status": enums.RoomStatus.EMPTY
                            },
                            {
                                "name": "B2",
                                "status": enums.RoomStatus.EMPTY
                            },
                            {"name": "B3",
                             "status": enums.RoomStatus.EMPTY
                             },
                            {
                                "name": "B4",
                                "status": enums.RoomStatus.EMPTY
                            },

                        ],
                        "room_id"
                    ),
                    "beds": ModelData(
                        models.RoomBed,
                        [
                            {"bed_type_id": _bed_type([models.BedType.type == "Single bed"])},
                            {"bed_type_id": _bed_type([models.BedType.type == "Double bed"])},
                        ],
                        "room_id"
                    ),
                    "photos": ModelData(
                        models.RoomPhoto,
                        [
                            {"photo_id": _photo([models.DocFile.name == "demo_property_image_21.jpg"])},
                            {"photo_id": _photo([models.DocFile.name == "demo_property_image_22.jpg"])},
                            {"photo_id": _photo([models.DocFile.name == "demo_property_image_23.jpg"])},
                            {"photo_id": _photo([models.DocFile.name == "demo_property_image_24.jpg"])},
                        ],
                        'room_id'
                    ),
                    "services": ModelData(
                        models.RoomService,
                        [
                            {"service_id": _service([models.Service.service_name == "Toothbrush",
                                                     models.ServiceCategory.category_name == "Bathroom"])},
                            {"service_id": _service([models.Service.service_name == "Iron",
                                                     models.ServiceCategory.category_name == "Facilities"])},
                            {"service_id": _service([models.Service.service_name == "Pajamas",
                                                     models.ServiceCategory.category_name == "Facilities"])},
                            {"service_id": _service([models.Service.service_name == "Towels",
                                                     models.ServiceCategory.category_name == "Bathroom"])},
                            {"service_id": _service([models.Service.service_name == "Shower",
                                                     models.ServiceCategory.category_name == "Bathroom"])},
                        ],
                        'room_id'
                    ),
                }
            ],
            'property_id'
        )

    }
    DATAS.append(property_data)

model_data = ModelData(
    models.Property,
    data=DATAS,
    check_records=True
)
