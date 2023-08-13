from pydantic import UUID4, BaseModel, ConfigDict, Field
from src.api.v1.dishes.schemas import Dish


class SubmenuBase(BaseModel):
    title: str
    description: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class Submenu(SubmenuBase):
    id: UUID4
    menu_id: UUID4


class SubmenuCount(Submenu):
    dishes_count: int = Field(default=0)


class NewSubmenu(SubmenuBase):
    pass


class SubmenuFull(Submenu):
    dishes: list[Dish] = Field(default=[])
