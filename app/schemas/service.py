from app.schemas.base import TranslatableModel


class Service(TranslatableModel):
    id: int
    service_name: str
    is_checked: bool = False

    class Config:
        orm_mode = True


class ServiceCategory(TranslatableModel):
    id: int
    category_name: str
    count: int = 0
    is_property_service_category: bool
    services: list["Service"] = []

    class Config:
        orm_mode = True
