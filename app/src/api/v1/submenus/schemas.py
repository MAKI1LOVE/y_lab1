from pydantic import UUID4, BaseModel, ConfigDict, Field


class SubMenu(BaseModel):
    id: UUID4
    menu_id: UUID4
    title: str
    description: str
    dishes_count: int = Field(default=0)

    model_config = ConfigDict(
        from_attributes=True
    )


class NewSubmenu(BaseModel):
    title: str
    description: str

    model_config = ConfigDict(
        from_attributes=True
    )
