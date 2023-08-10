from uuid import UUID

from aioredis import Redis


async def clear_dish_cache(redis: Redis, menu_uuid: UUID, submenu_uuid: UUID):
    await redis.delete(f'menu_{menu_uuid}_submenu_{submenu_uuid}_dishes')
    await redis.delete(f'menu_{menu_uuid}_submenu_{submenu_uuid}')
    await redis.delete(f'menu_{menu_uuid}_submenus')
    await redis.delete(f'menu_{menu_uuid}')
    await redis.delete('menus')
