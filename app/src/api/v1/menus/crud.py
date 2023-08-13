from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import Row, delete, func, join, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager
from sqlalchemy.sql.functions import coalesce
from src.api.v1.dishes.models import Dishes
from src.api.v1.menus.models import Menus
from src.api.v1.submenus.models import Submenus
from src.utils import get_session_deco


@get_session_deco
async def get_all_menus(session: AsyncSession) -> Sequence[Row]:
    """
    SELECT m.id, m.title, m.description, COUNT(t.id) AS submenus, SUM(COALESCE(t.dishes, 0)) AS dishes
        FROM menus AS m
        LEFT OUTER JOIN (
            SELECT s.id, s.menu_id, COUNT(d.id) AS dishes
                FROM submenus AS s
                LEFT OUTER JOIN dishes AS d ON d.submenu_id=s.id
                GROUP BY s.id, s.menu_id
        ) as t ON t.menu_id=m.id
        GROUP BY m.id, m.title, m.description;
    :param session:
    :return:
    """
    subq = select(
        Submenus.id,
        Submenus.menu_id,
        func.count(Dishes.id).label('dishes')
    ).select_from(
        join(
            left=Submenus,
            right=Dishes,
            isouter=True
        )
    ).group_by(Submenus.id, Submenus.menu_id)

    # print(subq)
    stmt = select(
        Menus.id, Menus.title, Menus.description,
        func.count(subq.c.id).label('submenus_count'),
        func.sum(coalesce(subq.c.dishes, 0)).label('dishes_count')
    ).select_from(
        join(
            left=Menus,
            right=subq,
            onclause=Menus.id == subq.c.menu_id,
            isouter=True
        )
    ).group_by(Menus)

    return (await session.execute(stmt)).all()


@get_session_deco
async def add_menu(title: str, description: str, session: AsyncSession) -> Row:
    stmt = insert(Menus).values({
        'title': title,
        'description': description
    }).returning(Menus.id, Menus.title, Menus.description)

    return (await session.execute(stmt)).one_or_none()


@get_session_deco
async def get_menu_by_id(menu_uuid: uuid.UUID, session: AsyncSession) -> Row | None:
    f"""
    SELECT m.id, m.title, m.description, COUNT(t.id) AS submenus, SUM(COALESCE(t.dishes, 0)) AS dishes
        FROM menus AS m
        LEFT OUTER JOIN (
            SELECT s.id, s.menu_id, COUNT(d.id) AS dishes
                FROM submenus AS s
                LEFT OUTER JOIN dishes AS d ON d.submenu_id=s.id
                GROUP BY s.id, s.menu_id
        ) as t ON t.menu_id=m.id
        WHERE m.id == {menu_uuid}
        GROUP BY m.id, m.title, m.description;
    :param menu_uuid:
    :param session:
    :return:
    """
    subq = select(
        Submenus.id,
        Submenus.menu_id,
        func.count(Dishes.id).label('dishes')
    ).select_from(
        join(
            left=Submenus,
            right=Dishes,
            isouter=True
        )
    ).group_by(Submenus.id, Submenus.menu_id)

    stmt = select(
        Menus.id, Menus.title, Menus.description,
        func.count(subq.c.id).label('submenus_count'),
        # SADeprecationWarning: The SelectBase.c and SelectBase.columns attributes are deprecated and will be removed in a future release; these attributes implicitly create a subquery that should be explicit.  Please call SelectBase.subquery() first in order to create a subquery, which then contains this attribute.  To access the columns that this SELECT object SELECTs from, use the SelectBase.selected_columns attribute.
        func.sum(coalesce(subq.c.dishes, 0)).label('dishes_count'),  # up
    ).select_from(
        join(
            left=Menus,
            right=subq,
            onclause=Menus.id == subq.c.menu_id,  # up
            isouter=True
        )
    ).where(
        Menus.id == menu_uuid
    ).group_by(Menus)

    return (await session.execute(stmt)).one_or_none()


@get_session_deco
async def update_menu(menu_uuid: uuid.UUID, title: str, description: str, session: AsyncSession) -> Row | None:
    stmt = update(Menus) \
        .where(Menus.id == menu_uuid) \
        .values(
        {
            Menus.title: title,
            Menus.description: description
        }
    ).returning(Menus.id, Menus.title, Menus.description)

    return (await session.execute(stmt)).one_or_none()


@get_session_deco
async def delete_menu_by_id(menu_uuid: uuid.UUID, session: AsyncSession):
    stmt = delete(Menus).where(Menus.id == menu_uuid)

    return await session.execute(stmt)


@get_session_deco
async def get_menus_full(session: AsyncSession):
    stmt = select(
        Menus
    ).select_from(
        join(
            left=Menus,
            right=Submenus,
            isouter=True,
        ).join(
            right=Dishes,
            isouter=True,
        )
    ).options(
        contains_eager(Menus.submenus).contains_eager(Submenus.dishes)
    )

    return (await session.execute(stmt)).unique().all()
