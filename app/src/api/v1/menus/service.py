from uuid import UUID

from aioredis import Redis
from fastapi import HTTPException, status
from src.api.v1.menus.crud import (
    add_menu,
    delete_menu_by_id,
    get_all_menus,
    get_menu_by_id,
    get_menus_full,
    update_menu,
)
from src.api.v1.menus.exceptions import menu_not_found
from src.api.v1.menus.schemas import MenuFull, MenuWithCount, NewMenu
from src.utils import delete_all_keys, get_db_data, set_key


async def get_all_menus_service(redis: Redis) -> list[MenuWithCount]:
    menus_stored = await get_db_data(redis, 'menus', get_all_menus)

    if menus_stored is None:
        return []

    menus = [MenuWithCount.model_validate(menu) for menu in menus_stored]
    await set_key(redis, 'menus', menus)

    return menus


async def create_menu_service(redis: Redis, new_menu: NewMenu) -> MenuWithCount:
    menu_db = await add_menu(new_menu.title, new_menu.description)
    if menu_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='smth bad'
        )

    menu = MenuWithCount.model_validate(menu_db)
    await set_key(redis, f'menu_{menu.id}', menu)
    await redis.delete('menus')

    return menu


async def get_menu_service(redis: Redis, menu_uuid: UUID) -> MenuWithCount:
    menu_stored = await get_db_data(redis, f'menu_{menu_uuid}', get_menu_by_id, menu_uuid)

    if menu_stored is None:
        await menu_not_found()

    menu = MenuWithCount.model_validate(menu_stored)
    await set_key(redis, f'menu_{menu.id}', menu)
    return menu


async def patch_menu_service(redis: Redis, menu_uuid: UUID, new_menu: NewMenu) -> MenuWithCount:
    updated_menu_db = await update_menu(menu_uuid, new_menu.title, new_menu.description)
    if updated_menu_db is None:
        await menu_not_found()

    menu = MenuWithCount.model_validate(updated_menu_db)

    await set_key(redis, f'menu_{menu.id}', menu)
    await redis.delete('menus')

    return menu


async def delete_menu_service(redis: Redis, menu_uuid: UUID) -> None:
    await delete_all_keys(redis, f'menu_{menu_uuid}')
    await redis.delete('menus')
    await delete_menu_by_id(menu_uuid)


async def get_menus_full_service():
    menus_db = await get_menus_full()

    menus = [MenuFull.model_validate(menu.Menus) for menu in menus_db]
    return menus
