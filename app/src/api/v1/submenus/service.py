from uuid import UUID

from aioredis import Redis
from fastapi import HTTPException, status
from src.api.v1.submenus.crud import (
    add_submenu,
    delete_submenu_by_id,
    get_all_submenus,
    get_submenu_by_id,
    update_submenu,
)
from src.api.v1.submenus.exceptions import submenu_not_found
from src.api.v1.submenus.redis import clear_submenus_cache
from src.api.v1.submenus.schemas import NewSubmenu, SubmenuCount
from src.utils import delete_all_keys, get_db_data, set_key


async def get_submenus_service(redis: Redis, menu_uuid: UUID) -> list[SubmenuCount]:
    submenus_stored = await get_db_data(redis, f'menu_{menu_uuid}_submenus', get_all_submenus, menu_uuid)
    if submenus_stored is None:
        return []

    submenus = [SubmenuCount.model_validate(submenu) for submenu in submenus_stored]
    await set_key(redis, f'menu_{menu_uuid}_submenus', submenus)

    return submenus


async def create_submenu_service(redis: Redis, menu_uuid: UUID, new_submenu: NewSubmenu) -> SubmenuCount:
    submenu_db = await add_submenu(menu_uuid, new_submenu.title, new_submenu.description)
    if submenu_db is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='smth bad'
        )

    submenu = SubmenuCount.model_validate(submenu_db)

    await set_key(redis, f'menu_{menu_uuid}_submenu_{submenu.id}', submenu)
    await clear_submenus_cache(redis, menu_uuid)

    return submenu


async def get_submenu_service(redis: Redis, menu_uuid: UUID, submenu_uuid: UUID) -> SubmenuCount:
    submenu_stored = await get_db_data(redis, f'menu_{menu_uuid}_submenu_{submenu_uuid}', get_submenu_by_id,
                                       menu_uuid, submenu_uuid)
    if submenu_stored is None:
        await submenu_not_found()

    submenu = SubmenuCount.model_validate(submenu_stored)
    await set_key(redis, f'menu_{menu_uuid}_submenu_{submenu.id}', submenu)

    return submenu


async def patch_submenu_service(
        redis: Redis,
        menu_uuid: UUID,
        submenu_uuid: UUID,
        new_submenu: NewSubmenu
) -> SubmenuCount:
    updated_submenu_db = await update_submenu(menu_uuid, submenu_uuid, new_submenu.title, new_submenu.description)
    if updated_submenu_db is None:
        await submenu_not_found()

    submenu = SubmenuCount.model_validate(updated_submenu_db)

    await set_key(redis, f'menu_{menu_uuid}_submenu_{submenu.id}', submenu)
    await redis.delete(f'menu_{menu_uuid}_submenus')

    return submenu


async def delete_submenu_service(redis, menu_uuid: UUID, submenu_uuid: UUID) -> None:
    await delete_all_keys(redis, f'menu_{menu_uuid}_submenu_{submenu_uuid}')
    await clear_submenus_cache(redis, menu_uuid)
    await delete_submenu_by_id(menu_uuid, submenu_uuid)
