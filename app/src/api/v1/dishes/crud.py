from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.v1.dishes.models import Dishes
from src.api.v1.submenus.models import Submenus
from src.utils import get_session_deco


@get_session_deco
async def get_all_dishes(submenu_uuid: UUID, session: AsyncSession):
    stmt = select(
        Dishes.id, Dishes.title, Dishes.description, Dishes.price, Dishes.submenu_id,
    ).where(
        Dishes.submenu_id == submenu_uuid and Dishes.submenu_id == Submenus.id
    )

    return (await session.execute(stmt)).all()


@get_session_deco
async def add_dish(submenu_uuid: UUID, title: str, description: str, price: str, session: AsyncSession):
    stmt = insert(
        Dishes
    ).values(
        {
            'submenu_id': submenu_uuid,
            'title': title,
            'description': description,
            'price': price
        }
    ).returning(Dishes.id, Dishes.title, Dishes.description, Dishes.price, Dishes.submenu_id,)

    return (await session.execute(stmt)).one_or_none()


@get_session_deco
async def get_dish_by_id(dish_uuid: UUID, session: AsyncSession):
    stmt = select(
        Dishes.id, Dishes.title, Dishes.description, Dishes.price, Dishes.submenu_id,
    ).where(
        Dishes.id == dish_uuid
    )

    return (await session.execute(stmt)).one_or_none()


@get_session_deco
async def update_dish(dish_uuid: UUID, title: str, description: str, price: str, session: AsyncSession):
    stmt = update(
        Dishes
    ).values(
        {
            Dishes.title: title,
            Dishes.description: description,
            Dishes.price: price
        }
    ).where(
        Dishes.id == dish_uuid
    ).returning(Dishes.id, Dishes.title, Dishes.description, Dishes.price, Dishes.submenu_id,)

    return (await session.execute(stmt)).one_or_none()


@get_session_deco
async def delete_dish_by_id(dish_uuid: UUID, session: AsyncSession):
    stmt = delete(
        Dishes
    ).where(
        Dishes.id == dish_uuid
    )

    return await session.execute(stmt)
