from _decimal import Decimal, InvalidOperation
from pydantic import UUID4, UUID5, BaseModel, ConfigDict, field_validator


class DishBase(BaseModel):
    title: str
    description: str
    price: str

    model_config = ConfigDict(
        from_attributes=True
    )

    @field_validator('price')
    def convert_price(cls, v):
        try:
            num = Decimal(v)
        except InvalidOperation:
            raise ValueError('not valid price')

        if num < 0:
            raise ValueError('not valid price')

        return str(num.quantize(Decimal('0.00')))


class Dish(DishBase):
    id: UUID4 | UUID5
    submenu_id: UUID4 | UUID5


class NewDish(DishBase):
    pass
