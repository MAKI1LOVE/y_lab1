from uuid import UUID

from aioredis import Redis
from fastapi import BackgroundTasks, HTTPException, status
from src.api.v1.menus.crud import (
    add_menu,
    delete_menu_by_id,
    get_all_menus,
    get_menu_by_id,
    get_menus_full,
    update_menu,
)
from src.api.v1.menus.exceptions import menu_not_found
from src.api.v1.menus.redis import (
    clear_and_set_menu_cache_after_create,
    clear_menu_cache_after_delete,
    clear_menu_cache_after_patch,
    set_menu_cache_after_get,
    set_menus_cache_after_get,
)
from src.api.v1.menus.schemas import MenuFull, MenuWithCount, NewMenu
from src.utils import get_db_data


async def get_all_menus_service(redis: Redis, bg_tasks: BackgroundTasks) -> list[MenuWithCount]:
    menus_stored = await get_db_data(redis, 'menus', get_all_menus)

    if menus_stored is None:
        return []

    menus = [MenuWithCount.model_validate(menu) for menu in menus_stored]
    bg_tasks.add_task(set_menus_cache_after_get, redis, menus)

    return menus


async def create_menu_service(redis: Redis, new_menu: NewMenu, bg_tasks: BackgroundTasks) -> MenuWithCount:
    menu_db = await add_menu(new_menu.title, new_menu.description)
    if menu_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='smth bad'
        )

    menu = MenuWithCount.model_validate(menu_db)
    bg_tasks.add_task(clear_and_set_menu_cache_after_create, redis, menu.id, menu)

    return menu


async def get_menu_service(redis: Redis, menu_uuid: UUID, bg_tasks: BackgroundTasks) -> MenuWithCount:
    menu_stored = await get_db_data(redis, f'menu_{menu_uuid}', get_menu_by_id, menu_uuid)

    if menu_stored is None:
        await menu_not_found()

    menu = MenuWithCount.model_validate(menu_stored)
    bg_tasks.add_task(set_menu_cache_after_get, redis, menu_uuid, menu)

    return menu


async def patch_menu_service(
        redis: Redis,
        menu_uuid: UUID,
        new_menu: NewMenu,
        bg_tasks: BackgroundTasks
) -> MenuWithCount:
    updated_menu_db = await update_menu(menu_uuid, new_menu.title, new_menu.description)

    if updated_menu_db is None:
        await menu_not_found()

    menu = MenuWithCount.model_validate(updated_menu_db)
    bg_tasks.add_task(clear_menu_cache_after_patch, redis, menu.id, menu)

    return menu


async def delete_menu_service(redis: Redis, menu_uuid: UUID, bg_tasks: BackgroundTasks) -> None:
    bg_tasks.add_task(clear_menu_cache_after_delete, redis, menu_uuid)
    await delete_menu_by_id(menu_uuid)


async def get_menus_full_service():
    menus_db = await get_menus_full()

    menus = [MenuFull.model_validate(menu.Menus) for menu in menus_db]
    return menus
