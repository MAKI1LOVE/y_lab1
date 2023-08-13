from pydantic import UUID4, BaseModel, ConfigDict, Field
from src.api.v1.submenus.schemas import SubmenuFull


class BaseMenu(BaseModel):
    title: str
    description: str

    model_config = ConfigDict(
        from_attributes=True
    )


class Menu(BaseMenu):
    id: UUID4


class MenuWithCount(Menu):
    submenus_count: int = Field(default=0)
    dishes_count: int = Field(default=0)


class NewMenu(BaseMenu):
    pass


class MenuFull(Menu):
    submenus: list[SubmenuFull] = Field(default=[])
