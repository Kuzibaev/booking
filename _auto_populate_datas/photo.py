from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DocFile
from app.utils.file import save_file
from ._conf import ModelData as ModelData_, HOTELS

_ASSETS_DIR = Path(__file__).parent / 'assets'

DATAS = [
    *[
        {'name': f'demo_property_image_{idx}.jpg', 'type': 'image/jpeg'}
        for idx in range(1, 11)
    ],
    {'name': 'article_demo_image.jpg', 'type': 'image/jpeg'},
    {'name': 'demo_hotel.png', 'type': 'image/jpeg'},
    *[
        {'name': f'demo_property_image_{idx}.jpg', 'type': 'image/jpeg'}
        for idx in range(20, 31)
    ],
    *[
        {'name': 'service_wi_fi.png', 'type': 'image/png'},
        {'name': 'service_swimming_pool.png', 'type': 'image/png'},
        {'name': 'service_sauna.png', 'type': 'image/png'},
        {'name': 'service_conference_hall.png', 'type': 'image/png'},
        {'name': 'service_non_smoking_rooms.png', 'type': 'image/png'},
        {'name': 'service_family_rooms.png', 'type': 'image/png'},
        {'name': 'service_garden.png', 'type': 'image/png'},
        {'name': 'service_terrace.png', 'type': 'image/png'},
        {'name': 'service_master_card_payment.png', 'type': 'image/png'},
        {'name': 'service_visa_card_payment.png', 'type': 'image/png'},
        {'name': 'service_smoking_rooms.png', 'type': 'image/png'},

        {'name': 'service_business_centre.png', 'type': 'image/png'},
        {'name': 'service_elevator_lift.png', 'type': 'image/png'},
        {'name': 'service_flat_screen_tv.png', 'type': 'image/png'},
        {'name': 'service_electric_vehicle_charging_station.png', 'type': 'image/png'},

        {'name': 'service_hot_tub_jacuzzi.png', 'type': 'image/png'},
        {'name': 'service_fitness.png', 'type': 'image/png'},
        {'name': 'service_massage.png', 'type': 'image/png'},
        {'name': 'service_cosmetology.png', 'type': 'image/png'},
        {'name': 'service_spa.png', 'type': 'image/png'},
        {'name': 'service_yoga.png', 'type': 'image/png'},
        {'name': 'service_massage_chair.png', 'type': 'image/png'},
        {'name': 'service_children_s_swimming_pool.png', 'type': 'image/png'},
        {'name': 'service_hydromassage_bath.png', 'type': 'image/png'},
        {'name': 'service_sun_loungers_beach_chairs.png', 'type': 'image/png'},
        {'name': 'service_parasols.png', 'type': 'image/png'},
        {'name': 'service_steam_room.png', 'type': 'image/png'},
        {'name': 'service_personal_coach.png', 'type': 'image/png'},
        {'name': 'service_turkish_sauna.png', 'type': 'image/png'},
        {'name': 'service_solarium.png', 'type': 'image/png'},
        {'name': 'service_onsen.png', 'type': 'image/png'},
        {'name': 'service_public_baths.png', 'type': 'image/png'},

        {'name': 'service_restaurant.png', 'type': 'image/png'},
        {'name': 'service_restaurant_(buffet).png', 'type': 'image/png'},
        {'name': 'service_bar.png', 'type': 'image/png'},
        {'name': 'service_delivery_of_products_(extra_charge).png', 'type': 'image/png'},
        {'name': 'service_vending_machine_(drinks).png', 'type': 'image/png'},
        {'name': 'service_vending_machine_(snacks).png', 'type': 'image/png'},
        {'name': 'service_diet_menus_(on_request).png', 'type': 'image/png'},
        {'name': 'service_delivery_of_food_to_the_room.png', 'type': 'image/png'},
        {'name': 'service_breakfast_delivery_to_the_room_(on_request).png', 'type': 'image/png'},
        {'name': 'service_snack_bar.png', 'type': 'image/png'},
        {'name': 'service_bbq_facilities.png', 'type': 'image/png'},
        {'name': 'service_packed_lunches_(on_request).png', 'type': 'image/png'},
        {'name': 'service_on_site_coffee_shop.png', 'type': 'image/png'},
        {'name': 'service_fruits.png', 'type': 'image/png'},
        {'name': 'service_menu_for_kids.png', 'type': 'image/png'},
        {'name': 'service_national_sweets.png', 'type': 'image/png'},

        {'name': 'service_night_club_dj.png', 'type': 'image/png'},
        {'name': 'service_new_year_show_programs.png', 'type': 'image/png'},
        {'name': 'service_karaoke.png', 'type': 'image/png'},
        {'name': 'service_children_s_club.png', 'type': 'image/png'},
        {'name': 'service_children_playground.png', 'type': 'image/png'},
        {'name': 'service_children_s_tv_channels.png', 'type': 'image/png'},
        {'name': 'service_indoor_play_area.png', 'type': 'image/png'},
        {'name': 'service_board_games_and_or_puzzles.png', 'type': 'image/png'},
        {'name': 'service_childcare_services.png', 'type': 'image/png'},
        {'name': 'service_baby_carriage.png', 'type': 'image/png'},
        {'name': 'service_evening_program.png', 'type': 'image/png'},

        {'name': 'service_basketball_court.png', 'type': 'image/png'},
        {'name': 'service_bowling.png', 'type': 'image/png'},
        {'name': 'service_tennis_court.png', 'type': 'image/png'},
        {'name': 'service_billiards.png', 'type': 'image/png'},
        {'name': 'service_table_tennis.png', 'type': 'image/png'},
        {'name': 'service_horseback_riding.png', 'type': 'image/png'},
        {'name': 'service_equipment_for_badminton.png', 'type': 'image/png'},
        {'name': 'service_beach.png', 'type': 'image/png'},
        {'name': 'service_darts.png', 'type': 'image/png'},
        {'name': 'service_aquapark.png', 'type': 'image/png'},
        {'name': 'service_stand_up_comedy.png', 'type': 'image/png'},
        {'name': 'service_movie_evenings.png', 'type': 'image/png'},
        {'name': 'service_cycling.png', 'type': 'image/png'},
        {'name': 'service_live_sporting_events.png', 'type': 'image/png'},

        {'name': 'service_dry_cleaning_(extra_charge).png', 'type': 'image/png'},
        {'name': 'service_dry_cleaning.png', 'type': 'image/png'},
        {'name': 'service_ironing_service_(extra_charge).png', 'type': 'image/png'},
        {'name': 'service_ironing_service.png', 'type': 'image/png'},
        {'name': 'service_laundry_(extra_charge).png', 'type': 'image/png'},
        {'name': 'service_laundry.png', 'type': 'image/png'},
        {'name': 'service_shoe_shine.png', 'type': 'image/png'},
        {'name': 'service_daily_cleaning.png', 'type': 'image/png'},
        {'name': 'service_trouser_press.png', 'type': 'image/png'},

        {'name': 'service_shops_on_site.png', 'type': 'image/png'},
        {'name': 'service_mini_market_on_site.png', 'type': 'image/png'},
        {'name': 'service_gift_shop.png', 'type': 'image/png'},

        {'name': 'service_smoke_free_property.png', 'type': 'image/png'},
        {'name': 'service_honeymoon_suite.png', 'type': 'image/png'},
        {'name': 'service_vip_room_facilities.png', 'type': 'image/png'},
        {'name': 'service_call_an_ambulance.png', 'type': 'image/png'},
        {'name': 'service_first_aid_kit.png', 'type': 'image/png'},
        {'name': 'service_animal_placement_extra_charge.png', 'type': 'image/png'},
        {'name': 'service_pet_basket.png', 'type': 'image/png'},
        {'name': 'service_24_hour_security.png', 'type': 'image/png'},
        {'name': 'service_smoke_detectors.png', 'type': 'image/png'},
        {'name': 'service_cctv_video_monitoring_outside_the_building.png', 'type': 'image/png'},
        {'name': 'service_fire_extinguishers.png', 'type': 'image/png'},
        {'name': 'service_hypoallergenic_room.png', 'type': 'image/png'},

        {'name': 'service_covered_parking.png', 'type': 'image/png'},
        {'name': 'service_bicycles_for_rent.png', 'type': 'image/png'},
        {'name': 'service_shuttle.png', 'type': 'image/png'},
        {'name': 'service_secure_parking.png', 'type': 'image/png'},
        {'name': 'service_street_parking.png', 'type': 'image/png'},
        {'name': 'service_taxi_ordering.png', 'type': 'image/png'},
        {'name': 'service_shuttle_(extra_charge).png', 'type': 'image/png'},
        {'name': 'service_transfer_to_the_ski_slope.png', 'type': 'image/png'},
        {'name': 'service_bicycle_(free_of_charge).png', 'type': 'image/png'},
        {'name': 'service_bicycle_rental_(extra_charge).png', 'type': 'image/png'},
        {'name': 'service_car_rental.png', 'type': 'image/png'},

        {'name': 'service_fax_photocopying.png', 'type': 'image/png'},
        {'name': 'service_concierge_service.png', 'type': 'image/png'},
        {'name': 'service_24_hour_front_desk.png', 'type': 'image/png'},
        {'name': 'service_express_check_in_check_out.png', 'type': 'image/png'},
        {'name': 'service_private_check_in_check_out.png', 'type': 'image/png'},
        {'name': 'service_tour_desk_(extra_charge).png', 'type': 'image/png'},
        {'name': 'service_currency_exchange.png', 'type': 'image/png'},
        {'name': 'service_ticket_service.png', 'type': 'image/png'},
        {'name': 'service_atm_cash_machine_on_site.png', 'type': 'image/png'},
        {'name': 'service_guide_service_(extra_charge).png', 'type': 'image/png'},
        {'name': 'service_parking_by_staff.png', 'type': 'image/png'},
        {'name': 'service_newspapers.png', 'type': 'image/png'},
        {'name': 'service_brochures_and_guides.png', 'type': 'image/png'},
        {'name': 'service_baggage_storage.png', 'type': 'image/png'},

        {'name': 'service_swimming_place.png', 'type': 'image/png'},
        {'name': 'service_designated_smoking_area.png', 'type': 'image/png'},
        {'name': 'service_sun_terrace.png', 'type': 'image/png'},
        {'name': 'service_shared_kitchen.png', 'type': 'image/png'},
        {'name': 'service_picnic_area.png', 'type': 'image/png'},
        {'name': 'service_library.png', 'type': 'image/png'},
        {'name': 'service_mosque_church_temple.png', 'type': 'image/png'},
        {'name': 'service_shared_lounge_with_tv_set.png', 'type': 'image/png'},
        {'name': 'service_garden_furniture.png', 'type': 'image/png'},

    ]
]
for hotel in HOTELS:
    for photo_num, photo in enumerate(hotel['photos']):
        extension = photo.rsplit('.', maxsplit=1)[1]
        DATAS.append({
            "name": f"{hotel['slug']}_{photo_num}.{extension}",
            "type": f"image/{extension.lower()}"
        })


class ModelData(ModelData_):
    async def save(self, session: AsyncSession, parent_id: int = None):
        if self.check_records:
            if await self.record_exist(session):
                return
        _instances = []
        for dict_ in self.data:
            file_name = dict_['name']
            file_path = _ASSETS_DIR / file_name
            await save_file(file_path, override=True, file_path="demo", is_auto_populate=True)
            _instances.append(self.model(
                **dict_,
                path=(Path("demo") / file_name).as_posix())
            )
        if _instances:
            session.add_all(_instances)
            await session.commit()


model_data = ModelData(
    DocFile,
    DATAS,
    check_records=True
)
