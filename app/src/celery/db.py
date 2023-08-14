from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.v1.dishes.models import Dishes
from src.api.v1.dishes.schemas import Dish
from src.api.v1.menus.models import Menus
from src.api.v1.menus.schemas import Menu
from src.api.v1.submenus.models import Submenus
from src.api.v1.submenus.schemas import Submenu
from src.utils import get_session_deco


async def update_db(menus: list[Menu], submenus: list[Submenu], dishes: list[Dish]):
    # clear tables
    await delete_all_menus([menu.id for menu in menus])
    await delete_all_submenus([submenu.id for submenu in submenus])
    await delete_all_dishes([dish.id for dish in dishes])

    # insert and update tables
    await insert_or_update_menus(menus)
    await insert_or_update_submenus(submenus)
    await insert_or_update_dishes(dishes)


@get_session_deco
async def insert_or_update_menus(menus: list[Menu], session: AsyncSession):
    stmt = insert(Menus).values(
        [menu.model_dump() for menu in menus]
    )

    stmt = stmt.on_conflict_do_update(
        index_elements=[stmt.excluded.id],
        set_={'title': stmt.excluded.title, 'description': stmt.excluded.description}
    )

    await session.execute(stmt)


@get_session_deco
async def insert_or_update_submenus(submenus: list[Submenu], session: AsyncSession):
    stmt = insert(Submenus).values(
        [submenu.model_dump() for submenu in submenus]
    )

    stmt = stmt.on_conflict_do_update(
        index_elements=[stmt.excluded.id],
        set_=dict(title=stmt.excluded.title, description=stmt.excluded.description, menu_id=stmt.excluded.menu_id)
    )

    await session.execute(stmt)


@get_session_deco
async def insert_or_update_dishes(dishes: list[Dish], session: AsyncSession):
    stmt = insert(Dishes).values(
        [dish.model_dump() for dish in dishes]
    )

    stmt = stmt.on_conflict_do_update(
        index_elements=[stmt.excluded.id],
        set_=dict(
            title=stmt.excluded.title,
            description=stmt.excluded.description,
            price=stmt.excluded.price,
            submenu_id=stmt.excluded.submenu_id,
        )
    )

    await session.execute(stmt)


@get_session_deco
async def delete_all_menus(menus_ids: list[UUID], session: AsyncSession):
    stmt = delete(Menus).where(Menus.id not in menus_ids)
    await session.execute(stmt)


@get_session_deco
async def delete_all_submenus(submenus_ids: list[UUID], session: AsyncSession):
    stmt = delete(Menus).where(Menus.id not in submenus_ids)
    await session.execute(stmt)


@get_session_deco
async def delete_all_dishes(dishes_ids: list[UUID], session: AsyncSession):
    stmt = delete(Menus).where(Menus.id not in dishes_ids)
    await session.execute(stmt)
