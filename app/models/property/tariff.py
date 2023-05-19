import sqlalchemy as sa
from app.models.base import Base


class Tariff(Base):
    is_breakfast_included = sa.Column(sa.Boolean, nullable=False)
    is_lunch_included = sa.Column(sa.Boolean, nullable=False)
    is_dinner_included = sa.Column(sa.Boolean, nullable=False)
    is_evening_meal_included = sa.Column(sa.Boolean, nullable=False)

    def __str__(self):
        return f'Tariff {self.id}'

    def __repr__(self):
        return self.__str__()
