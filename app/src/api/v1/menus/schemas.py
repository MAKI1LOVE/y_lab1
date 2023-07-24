from pydantic import BaseModel, UUID4, ConfigDict, Field


class Menu(BaseModel):
    id: UUID4
    title: str
    description: str
    submenus_count: int = Field(default=0)
    dishes_count: int = Field(default=0)

    model_config = ConfigDict(
        from_attributes=True
    )


class NewMenu(BaseModel):
    title: str
    description: str

    model_config = ConfigDict(
        from_attributes=True
    )
