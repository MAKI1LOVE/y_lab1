from uuid import UUID

from aioredis import Redis
from src.api.v1.menus.schemas import MenuWithCount
from src.utils import delete_all_keys, set_key


async def set_menus_cache_after_get(redis, menus: list[MenuWithCount]):
    await set_key(redis, 'menus', menus)


async def clear_and_set_menu_cache_after_create(redis: Redis, menu_uuid: UUID, menu: MenuWithCount):
    await set_key(redis, f'menu_{menu_uuid}', menu)
    await redis.delete('menus')


async def set_menu_cache_after_get(redis: Redis, menu_uuid: UUID, menu: MenuWithCount):
    await set_key(redis, f'menu_{menu_uuid}', menu)


async def clear_menu_cache_after_patch(redis: Redis, menu_uuid: UUID, menu: MenuWithCount):
    await set_key(redis, f'menu_{menu_uuid}', menu)
    await redis.delete('menus')


async def clear_menu_cache_after_delete(redis: Redis, menu_uuid: UUID):
    await delete_all_keys(redis, f'menu_{menu_uuid}')
    await redis.delete('menus')
