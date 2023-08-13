from uuid import UUID

from aioredis import Redis
from fastapi import BackgroundTasks, HTTPException, status
from src.api.v1.submenus.crud import (
    add_submenu,
    delete_submenu_by_id,
    get_all_submenus,
    get_submenu_by_id,
    update_submenu,
)
from src.api.v1.submenus.exceptions import submenu_not_found
from src.api.v1.submenus.redis import (
    clear_and_set_submenu_cache_after_create,
    clear_and_set_submenu_cache_after_patch,
    clear_submenu_cache_after_delete,
    set_submenu_cache_after_get,
    set_submenus_cache_after_get,
)
from src.api.v1.submenus.schemas import NewSubmenu, SubmenuCount
from src.utils import get_db_data


async def get_submenus_service(redis: Redis, menu_uuid: UUID, bg_tasks: BackgroundTasks) -> list[SubmenuCount]:
    submenus_stored = await get_db_data(redis, f'menu_{menu_uuid}_submenus', get_all_submenus, menu_uuid)

    if submenus_stored is None:
        return []

    submenus = [SubmenuCount.model_validate(submenu) for submenu in submenus_stored]
    bg_tasks.add_task(set_submenus_cache_after_get, redis, menu_uuid, submenus)

    return submenus


async def create_submenu_service(
        redis: Redis,
        menu_uuid: UUID,
        new_submenu: NewSubmenu,
        bg_tasks: BackgroundTasks,
) -> SubmenuCount:
    submenu_db = await add_submenu(menu_uuid, new_submenu.title, new_submenu.description)

    if submenu_db is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='smth bad'
        )

    submenu = SubmenuCount.model_validate(submenu_db)
    bg_tasks.add_task(clear_and_set_submenu_cache_after_create, redis, menu_uuid, submenu.id, submenu)

    return submenu


async def get_submenu_service(
        redis: Redis,
        menu_uuid: UUID,
        submenu_uuid: UUID,
        bg_tasks: BackgroundTasks
) -> SubmenuCount:
    submenu_stored = await get_db_data(redis, f'menu_{menu_uuid}_submenu_{submenu_uuid}', get_submenu_by_id,
                                       menu_uuid, submenu_uuid)
    if submenu_stored is None:
        await submenu_not_found()

    submenu = SubmenuCount.model_validate(submenu_stored)
    bg_tasks.add_task(set_submenu_cache_after_get, redis, menu_uuid, submenu_uuid, submenu)

    return submenu


async def patch_submenu_service(
        redis: Redis,
        menu_uuid: UUID,
        submenu_uuid: UUID,
        new_submenu: NewSubmenu,
        bg_tasks: BackgroundTasks,
) -> SubmenuCount:
    updated_submenu_db = await update_submenu(menu_uuid, submenu_uuid, new_submenu.title, new_submenu.description)

    if updated_submenu_db is None:
        await submenu_not_found()

    submenu = SubmenuCount.model_validate(updated_submenu_db)
    bg_tasks.add_task(clear_and_set_submenu_cache_after_patch, redis, menu_uuid, submenu_uuid, submenu)

    return submenu


async def delete_submenu_service(redis: Redis, menu_uuid: UUID, submenu_uuid: UUID, bg_tasks: BackgroundTasks) -> None:
    bg_tasks.add_task(clear_submenu_cache_after_delete, redis, menu_uuid, submenu_uuid)
    await delete_submenu_by_id(menu_uuid, submenu_uuid)
