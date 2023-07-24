from _decimal import InvalidOperation, Decimal

from pydantic import BaseModel, UUID4, field_validator, ConfigDict


class Dish(BaseModel):
    id: UUID4
    submenu_id: UUID4
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


class NewDish(BaseModel):
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