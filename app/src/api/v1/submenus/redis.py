from uuid import UUID

from aioredis import Redis


async def clear_submenus_cache(redis: Redis, menu_uuid: UUID):
    await redis.delete(f'menu_{menu_uuid}_submenus')
    await redis.delete(f'menu_{menu_uuid}')
    await redis.delete('menus')
