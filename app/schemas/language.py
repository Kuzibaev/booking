from .base import TranslatableModel


class Language(TranslatableModel):
    id: int
    lang_name: str

    class Config:
        orm_mode = True
