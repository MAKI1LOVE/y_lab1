from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import dishes_table, submenus_table
from src.dependencies import get_session_deco


@get_session_deco
async def get_all_dishes(submenu_uuid: UUID, session: AsyncSession):
    stmt = select(
        dishes_table
    ).where(
        dishes_table.c.submenu_id == submenu_uuid and dishes_table.c.submenu_id == submenus_table.c.id
    )

    return (await session.execute(stmt)).all()


@get_session_deco
async def add_dish(submenu_uuid: UUID, title: str, description: str, price: str, session: AsyncSession):
    stmt = insert(
        dishes_table
    ).values(
        {
            'submenu_id': submenu_uuid,
            'title': title,
            'description': description,
            'price': price
        }
    ).returning(dishes_table)

    return (await session.execute(stmt)).one_or_none()


@get_session_deco
async def get_dish_by_id(dish_uuid: UUID, session: AsyncSession):
    stmt = select(
        dishes_table
    ).where(
        dishes_table.c.id == dish_uuid
    )

    return (await session.execute(stmt)).one_or_none()


@get_session_deco
async def update_dish(dish_uuid: UUID, title: str, description: str, price: str, session: AsyncSession):
    stmt = update(
        dishes_table
    ).values(
        {
            dishes_table.c.title: title,
            dishes_table.c.description: description,
            dishes_table.c.price: price
        }
    ).where(
        dishes_table.c.id == dish_uuid
    ).returning(dishes_table)

    return (await session.execute(stmt)).one_or_none()


@get_session_deco
async def delete_dish_by_id(dish_uuid: UUID, session: AsyncSession):
    stmt = delete(
        dishes_table
    ).where(
        dishes_table.c.id == dish_uuid
    )

    return await session.execute(stmt)
