from __future__ import annotations

import uuid


class MenuFactory:
    def __init__(
            self,
            menu_uuid: uuid.UUID | None,
            title: str = '',
            description: str = '',
            submenus_count: int = 0,
            dishes_count: int = 0
    ):
        self.id = menu_uuid or uuid.uuid4()
        self.title = title or f'title_{self.id}'
        self.description = description or f'description_{self.id}'
        self.submenus_count = submenus_count
        self.dishes_count = dishes_count
