from uuid import UUID

from sqlalchemy import delete, func, join, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.v1.dishes.models import Dishes
from src.api.v1.submenus.models import Submenus
from src.utils import get_session_deco


@get_session_deco
async def get_all_submenus(menu_uuid: UUID, session: AsyncSession):
    stmt = select(
        Submenus.id, Submenus.title, Submenus.description, Submenus.menu_id,
        func.count(Dishes.id).label('dishes_count')
    ).select_from(
        join(
            left=Submenus,
            right=Dishes,
            isouter=True
        )
    ).where(
        Submenus.menu_id == menu_uuid
    ).group_by(
        Submenus
    )

    return (await session.execute(stmt)).all()


@get_session_deco
async def add_submenu(menu_uuid: UUID, title: str, description: str, session: AsyncSession):
    stmt = insert(Submenus).values(
        {
            'menu_id': menu_uuid,
            'title': title,
            'description': description
        }
    ).returning(Submenus.id, Submenus.title, Submenus.description, Submenus.menu_id)

    return (await session.execute(stmt)).one_or_none()


@get_session_deco
async def get_submenu_by_id(menu_uuid: UUID, submenu_uuid: UUID, session: AsyncSession):
    stmt = select(
        Submenus.id, Submenus.title, Submenus.description, Submenus.menu_id,
        func.count(Dishes.id).label('dishes_count')
    ).select_from(
        join(
            left=Submenus,
            right=Dishes,
            isouter=True
        )
    ).where(
        Submenus.id == submenu_uuid and Submenus.menu_id == menu_uuid
    ).group_by(Submenus)

    return (await session.execute(stmt)).one_or_none()


@get_session_deco
async def update_submenu(menu_uuid: UUID, submenu_uuid: UUID, title: str, description: str, session: AsyncSession):
    stmt = update(
        Submenus
    ).where(
        Submenus.menu_id == menu_uuid and Submenus.id == submenu_uuid
    ).values(
        {
            Submenus.title: title,
            Submenus.description: description
        }
    ).returning(Submenus.id, Submenus.title, Submenus.description, Submenus.menu_id)

    return (await session.execute(stmt)).one_or_none()


@get_session_deco
async def delete_submenu_by_id(menu_uuid: UUID, submenu_uuid: UUID, session: AsyncSession):
    stmt = delete(
        Submenus
    ).where(
        Submenus.menu_id == menu_uuid and Submenus.id == submenu_uuid
    )

    return await session.execute(stmt)
