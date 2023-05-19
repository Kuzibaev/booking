from datetime import date

from pydantic import BaseModel, Field

from app.schemas.base import PhoneNumber


class Contract(BaseModel):
    id: int
    contract_date: date
    contract_number: str
    firma_type: str
    city: str
    address: str
    zip_code: str
    phone: PhoneNumber
    payment_account: str
    usd_block: float
    oked: str
    bank: str
    mfo: str
    inn: str
    okonh: str
    based: str
    author: str

    class Config:
        orm_mode = True


class ContractCreateOrUpdate(BaseModel):
    contract_date: date = Field(...)
    contract_number: str
    firma_type: str
    city: str
    address: str
    zip_code: str
    phone: PhoneNumber
    payment_account: str
    usd_block: int = 0
    oked: str
    bank: str
    mfo: str
    inn: str
    okonh: str
    based: str
    author: str
