from uuid import UUID

from aioredis import Redis
from src.api.v1.submenus.schemas import SubmenuCount
from src.utils import delete_all_keys, set_key


async def set_submenus_cache_after_get(
        redis: Redis,
        menu_uuid: UUID,
        submenus: list[SubmenuCount],
):
    await set_key(redis, f'menu_{menu_uuid}_submenus', submenus)


async def clear_and_set_submenu_cache_after_create(
        redis: Redis,
        menu_uuid: UUID,
        submenu_uuid: UUID,
        submenu: SubmenuCount,
):
    await set_key(redis, f'menu_{menu_uuid}_submenu_{submenu_uuid}', submenu)
    await clear_submenus_cache(redis, menu_uuid)


async def set_submenu_cache_after_get(
        redis: Redis,
        menu_uuid: UUID,
        submenu_uuid: UUID,
        submenu: SubmenuCount,
):
    await set_key(redis, f'menu_{menu_uuid}_submenu_{submenu_uuid}', submenu)


async def clear_and_set_submenu_cache_after_patch(
        redis: Redis,
        menu_uuid: UUID,
        submenu_uuid: UUID,
        submenu: SubmenuCount,
):
    await set_key(redis, f'menu_{menu_uuid}_submenu_{submenu_uuid}', submenu)
    await redis.delete(f'menu_{menu_uuid}_submenus')


async def clear_submenu_cache_after_delete(redis: Redis, menu_uuid: UUID, submenu_uuid: UUID):
    await delete_all_keys(redis, f'menu_{menu_uuid}_submenu_{submenu_uuid}')
    await clear_submenus_cache(redis, menu_uuid)


async def clear_submenus_cache(redis: Redis, menu_uuid: UUID):
    await redis.delete(f'menu_{menu_uuid}_submenus')
    await redis.delete(f'menu_{menu_uuid}')
    await redis.delete('menus')
