from uuid import UUID

from sqlalchemy import delete, func, join, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import dishes_table, submenus_table
from src.dependencies import get_session_deco


@get_session_deco
async def get_all_submenus(menu_uuid: UUID, session: AsyncSession):
    stmt = select(
        submenus_table,
        func.count(dishes_table.c.id).label('dishes_count')
    ).select_from(
        join(
            left=submenus_table,
            right=dishes_table,
            isouter=True
        )
    ).where(
        submenus_table.c.menu_id == menu_uuid
    ).group_by(
        submenus_table
    )

    return (await session.execute(stmt)).all()


@get_session_deco
async def add_submenu(menu_uuid: UUID, title: str, description: str, session: AsyncSession):
    stmt = insert(submenus_table).values(
        {
            'menu_id': menu_uuid,
            'title': title,
            'description': description
        }
    ).returning(submenus_table)

    return (await session.execute(stmt)).one_or_none()


@get_session_deco
async def get_submenu_by_id(menu_uuid: UUID, submenu_uuid: UUID, session: AsyncSession):
    stmt = select(
        submenus_table,
        func.count(dishes_table.c.id).label('dishes_count')
    ).select_from(
        join(
            left=submenus_table,
            right=dishes_table,
            isouter=True
        )
    ).where(
        submenus_table.c.id == submenu_uuid and submenus_table.c.menu_id == menu_uuid
    ).group_by(submenus_table)

    return (await session.execute(stmt)).one_or_none()


@get_session_deco
async def update_submenu(menu_uuid: UUID, submenu_uuid: UUID, title: str, description: str, session: AsyncSession):
    stmt = update(
        submenus_table
    ).where(
        submenus_table.c.menu_id == menu_uuid and submenus_table.c.id == submenu_uuid
    ).values(
        {
            submenus_table.c.title: title,
            submenus_table.c.description: description
        }
    ).returning(submenus_table.c.id)

    return (await session.execute(stmt)).one_or_none()


@get_session_deco
async def delete_submenu_by_id(menu_uuid: UUID, submenu_uuid: UUID, session: AsyncSession):
    stmt = delete(
        submenus_table
    ).where(
        submenus_table.c.menu_id == menu_uuid and submenus_table.c.id == submenu_uuid
    )

    return await session.execute(stmt)
