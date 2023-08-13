from uuid import UUID

from aioredis import Redis
from src.api.v1.dishes.schemas import Dish
from src.utils import set_key


async def set_dishes_cache_after_get(
        redis: Redis,
        menu_uuid: UUID,
        submenu_uuid: UUID,
        dishes: list[Dish],
):
    await set_key(redis, f'menu_{menu_uuid}_submenu_{submenu_uuid}_dishes', dishes)


async def clear_and_set_dish_cache_after_create(
        redis: Redis,
        menu_uuid: UUID,
        submenu_uuid: UUID,
        dish_uuid: UUID,
        dish: Dish,
):
    await set_key(redis, f'menu_{menu_uuid}_submenu_{submenu_uuid}_dish_{dish_uuid}', dish)
    await clear_dish_cache(redis, menu_uuid, submenu_uuid)


async def set_dish_cache_after_get(
        redis: Redis,
        menu_uuid: UUID,
        submenu_uuid: UUID,
        dish_uuid: UUID,
        dish: Dish,
):
    await set_key(redis, f'menu_{menu_uuid}_submenu_{submenu_uuid}_dish_{dish_uuid}', dish)


async def clear_and_set_dish_cache_after_patch(
        redis: Redis,
        menu_uuid: UUID,
        submenu_uuid: UUID,
        dish_uuid: UUID,
        dish: Dish,
):
    await set_key(redis, f'menu_{menu_uuid}_submenu_{submenu_uuid}_dish_{dish_uuid}', dish)
    await redis.delete(f'menu_{menu_uuid}_submenu_{submenu_uuid}_dishes')


async def clear_dish_cache_after_delete(
        redis: Redis,
        menu_uuid: UUID,
        submenu_uuid: UUID,
        dish_uuid: UUID,
):
    await redis.delete(f'menu_{menu_uuid}_submenu_{submenu_uuid}_dish_{dish_uuid}')
    await clear_dish_cache(redis, menu_uuid, submenu_uuid)


async def clear_dish_cache(redis: Redis, menu_uuid: UUID, submenu_uuid: UUID):
    await redis.delete(f'menu_{menu_uuid}_submenu_{submenu_uuid}_dishes')
    await redis.delete(f'menu_{menu_uuid}_submenu_{submenu_uuid}')
    await redis.delete(f'menu_{menu_uuid}_submenus')
    await redis.delete(f'menu_{menu_uuid}')
    await redis.delete('menus')
