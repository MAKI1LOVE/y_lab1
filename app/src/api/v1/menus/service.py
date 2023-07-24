import uuid

from sqlalchemy import select, func, join, update, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import coalesce

from src.database import menus_table, submenus_table, dishes_table
from src.dependencies import get_session_deco


@get_session_deco
async def get_all_menus(session: AsyncSession):
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
        submenus_table.c.id,
        submenus_table.c.menu_id,
        func.count(dishes_table.c.id).label('dishes')
    ).select_from(
        join(
            left=submenus_table,
            right=dishes_table,
            isouter=True
        )
    ).group_by(submenus_table.c.id, submenus_table.c.menu_id)

    # print(subq)
    stmt = select(
        menus_table,
        func.count(subq.c.id).label('submenus_count'),
        func.sum(coalesce(subq.c.dishes, 0)).label('dishes_count')
    ).select_from(
        join(
            left=menus_table,
            right=subq,
            onclause=menus_table.c.id == subq.c.menu_id,
            isouter=True
        )
    ).group_by(menus_table)

    return (await session.execute(stmt)).all()


@get_session_deco
async def add_menu(title: str, description: str, session: AsyncSession):
    stmt = insert(menus_table).values({
        'title': title,
        'description': description
    }).returning(menus_table.c.id, menus_table.c.title, menus_table.c.description)

    return (await session.execute(stmt)).one_or_none()


@get_session_deco
async def get_menu_by_id(menu_uuid: uuid.UUID, session: AsyncSession):
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
        submenus_table.c.id,
        submenus_table.c.menu_id,
        func.count(dishes_table.c.id).label('dishes')
    ).select_from(
        join(
            left=submenus_table,
            right=dishes_table,
            isouter=True
        )
    ).group_by(submenus_table.c.id, submenus_table.c.menu_id)

    stmt = select(
        menus_table,
        func.count(subq.c.id).label('submenus_count'),
        # SADeprecationWarning: The SelectBase.c and SelectBase.columns attributes are deprecated and will be removed in a future release; these attributes implicitly create a subquery that should be explicit.  Please call SelectBase.subquery() first in order to create a subquery, which then contains this attribute.  To access the columns that this SELECT object SELECTs from, use the SelectBase.selected_columns attribute.
        func.sum(coalesce(subq.c.dishes, 0)).label('dishes_count')  # up
    ).select_from(
        join(
            left=menus_table,
            right=subq,
            onclause=menus_table.c.id == subq.c.menu_id,  # up
            isouter=True
        )
    ).where(
        menus_table.c.id == menu_uuid
    ).group_by(menus_table)

    return (await session.execute(stmt)).one_or_none()


@get_session_deco
async def update_menu(menu_uuid: uuid.UUID, title: str, description: str, session: AsyncSession):
    stmt = update(menus_table) \
        .where(menus_table.c.id == menu_uuid) \
        .values(
        {
            menus_table.c.title: title,
            menus_table.c.description: description
        }
    ).returning(menus_table.c.id)

    return (await session.execute(stmt)).one_or_none()


@get_session_deco
async def delete_menu_by_id(menu_uuid: uuid.UUID, session: AsyncSession):
    stmt = delete(menus_table).where(menus_table.c.id == menu_uuid)

    return await session.execute(stmt)
