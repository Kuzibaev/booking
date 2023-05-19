from typing import TypeVar, Generic, Any

import phonenumbers
from pydantic import BaseModel, root_validator
from pydantic.generics import GenericModel
from pydantic.utils import GetterDict
from pydantic.validators import strict_str_validator

from app.models.base import TranslationBase
from app.utils.i18n import translation

_ = translation.lazy_gettext

TypeT = TypeVar("TypeT")


def _get_translation_model_fields(model: TranslationBase):
    _exclude = {'id', 'created_at', 'updated_at', 'language', 'is_default'}
    return {
        k: v
        for k, v in model.__dict__.items()
        if not k.startswith("_") and k not in _exclude
    }


class TranslatableModel(BaseModel):
    class Config:
        orm_mode = True

    @root_validator(pre=True)
    def change_fields_to_current_language(cls, values: GetterDict):
        values = {**values}
        if 'translations' in values:
            translations: list = values.get('translations')
            for tr in translations:
                if tr.language.value == translation.current_locale:
                    values.update(_get_translation_model_fields(tr))
                    break
        return values


class DataResponse(GenericModel, Generic[TypeT]):
    total: int = 0
    items: list[TypeT | Any] = []

    class Config:
        orm_mode = True


class OrdersResponse(DataResponse):
    orders_of_today: int = 0
    orders_of_yesterday: int = 0
    orders_of_last_30_days: int = 0


class BookingsResponse(DataResponse):
    has_been_booked_count: int = 0
    active_status_count: int = 0


class PhoneNumber(str):
    @classmethod
    def __get_validators__(cls):
        yield strict_str_validator
        yield cls.validate

    @classmethod
    def validate(cls, v: str):
        v = v.strip().replace(' ', '')

        try:
            phone = phonenumbers.parse(v)
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValueError(_('Invalid phone number format'))

        return cls(phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164))
