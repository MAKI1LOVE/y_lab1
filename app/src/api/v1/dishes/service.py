from uuid import UUID

from aioredis import Redis
from fastapi import HTTPException, status
from src.api.v1.dishes.crud import (
    add_dish,
    delete_dish_by_id,
    get_all_dishes,
    get_dish_by_id,
    update_dish,
)
from src.api.v1.dishes.exceptions import dish_not_found
from src.api.v1.dishes.schemas import Dish, NewDish
from src.utils import get_db_data, set_key


async def get_all_dishes_service(redis: Redis, menu_uuid: UUID, submenu_uuid: UUID) -> list[Dish]:
    dishes_stored = await get_db_data(redis, f'menu_{menu_uuid}_submenu_{submenu_uuid}_dishes', get_all_dishes,
                                      submenu_uuid)
    if dishes_stored is None:
        return []

    dishes = [Dish.model_validate(dish) for dish in dishes_stored]
    await set_key(redis, f'menu_{menu_uuid}_submenu_{submenu_uuid}_dishes', dishes)

    return dishes


async def create_dish_service(redis: Redis, menu_uuid: UUID, submenu_uuid: UUID, new_dish: NewDish) -> Dish:
    dish_db = await add_dish(submenu_uuid, new_dish.title, new_dish.description, new_dish.price)
    if dish_db is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='smth bad'
        )

    dish = Dish.model_validate(dish_db)

    await set_key(redis, f'menu_{menu_uuid}_submenu_{submenu_uuid}_dish_{dish.id}', dish)
    await redis.delete(f'menu_{menu_uuid}_submenu_{submenu_uuid}_dishes')
    await redis.delete(f'menu_{menu_uuid}_submenu_{submenu_uuid}')
    await redis.delete(f'menu_{menu_uuid}_submenus')
    await redis.delete(f'menu_{menu_uuid}')
    await redis.delete('menus')

    return dish


async def get_dish_service(redis: Redis, menu_uuid: UUID, submenu_uuid: UUID, dish_uuid: UUID) -> Dish:
    dish_stored = await get_db_data(redis, f'menu_{menu_uuid}_submenu_{submenu_uuid}_dish_{dish_uuid}',
                                    get_dish_by_id, dish_uuid)
    if dish_stored is None:
        await dish_not_found()

    dish = Dish.model_validate(dish_stored)
    await set_key(redis, f'menu_{menu_uuid}_submenu_{submenu_uuid}_dish_{dish.id}', dish)

    return dish


async def patch_dish_service(redis: Redis, menu_uuid: UUID, submenu_uuid: UUID, dish_uuid: UUID, new_dish: NewDish) -> Dish:
    dish_db = await update_dish(dish_uuid, new_dish.title, new_dish.description, new_dish.price)
    if dish_db is None:
        await dish_not_found()

    dish = Dish.model_validate(dish_db)

    await set_key(redis, f'menu_{menu_uuid}_submenu_{submenu_uuid}_dish_{dish_uuid}', dish)
    await redis.delete(f'menu_{menu_uuid}_submenu_{submenu_uuid}_dishes')

    return dish


async def delete_dish_service(redis: Redis, menu_uuid: UUID, submenu_uuid: UUID, dish_uuid: UUID) -> None:
    await redis.delete(f'menu_{menu_uuid}_submenu_{submenu_uuid}_dish_{dish_uuid}')
    await redis.delete(f'menu_{menu_uuid}_submenu_{submenu_uuid}_dishes')
    await redis.delete(f'menu_{menu_uuid}_submenu_{submenu_uuid}')
    await redis.delete(f'menu_{menu_uuid}_submenus')
    await redis.delete(f'menu_{menu_uuid}')
    await redis.delete('menus')

    await delete_dish_by_id(dish_uuid)
