from typing import Annotated
from uuid import UUID

from aioredis import Redis
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from src.api.v1.dishes.exceptions import dish_not_found
from src.api.v1.dishes.schemas import Dish, NewDish
from src.api.v1.dishes.service import (
    add_dish,
    delete_dish_by_id,
    get_all_dishes,
    get_dish_by_id,
    update_dish,
)
from src.database import get_redis
from src.utils import get_db_data, set_key

dishes_router = APIRouter()


@dishes_router.get('', status_code=200, response_model=list[Dish])
async def get_dishes(
        menu_uuid: Annotated[UUID, Path()],
        submenu_uuid: Annotated[UUID, Path()],
        redis: Annotated[Redis, Depends(get_redis)],
):
    dishes_stored = await get_db_data(redis, f'menu_{menu_uuid}_submenu_{submenu_uuid}_dishes', get_all_dishes,
                                      submenu_uuid)
    if dishes_stored is None:
        return []

    dishes = [Dish.model_validate(dish) for dish in dishes_stored]
    await set_key(redis, f'menu_{menu_uuid}_submenu_{submenu_uuid}_dishes', dishes)

    return dishes


@dishes_router.post('', status_code=201, response_model=Dish)
async def create_dish(
        menu_uuid: Annotated[UUID, Path()],
        submenu_uuid: Annotated[UUID, Path()],
        new_dish: Annotated[NewDish, Body()],
        redis: Annotated[Redis, Depends(get_redis)],
):
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


@dishes_router.get('/{dish_uuid}', status_code=200, response_model=Dish)
async def get_dish(
        menu_uuid: Annotated[UUID, Path()],
        submenu_uuid: Annotated[UUID, Path()],
        dish_uuid: Annotated[UUID, Path()],
        redis: Annotated[Redis, Depends(get_redis)],
):
    dish_stored = await get_db_data(redis, f'menu_{menu_uuid}_submenu_{submenu_uuid}_dish_{dish_uuid}',
                                    get_dish_by_id, dish_uuid)
    if dish_stored is None:
        await dish_not_found()

    dish = Dish.model_validate(dish_stored)
    await set_key(redis, f'menu_{menu_uuid}_submenu_{submenu_uuid}_dish_{dish.id}', dish)

    return dish


@dishes_router.patch('/{dish_uuid}', status_code=200, response_model=Dish)
async def patch_dish(
        menu_uuid: Annotated[UUID, Path()],
        submenu_uuid: Annotated[UUID, Path()],
        dish_uuid: Annotated[UUID, Path()],
        new_dish: Annotated[NewDish, Body()],
        redis: Annotated[Redis, Depends(get_redis)],

):
    dish_db = await update_dish(dish_uuid, new_dish.title, new_dish.description, new_dish.price)
    if dish_db is None:
        await dish_not_found()

    dish = Dish.model_validate(dish_db)

    await set_key(redis, f'menu_{menu_uuid}_submenu_{submenu_uuid}_dish_{dish_uuid}', dish)
    await redis.delete(f'menu_{menu_uuid}_submenu_{submenu_uuid}_dishes')

    return dish


@dishes_router.delete('/{dish_uuid}', status_code=200)
async def delete_dish(
        menu_uuid: UUID,
        submenu_uuid: UUID,
        dish_uuid: UUID,
        redis: Annotated[Redis, Depends(get_redis)]
):
    await redis.delete(f'menu_{menu_uuid}_submenu_{submenu_uuid}_dish_{dish_uuid}')
    await redis.delete(f'menu_{menu_uuid}_submenu_{submenu_uuid}_dishes')
    await redis.delete(f'menu_{menu_uuid}_submenu_{submenu_uuid}')
    await redis.delete(f'menu_{menu_uuid}_submenus')
    await redis.delete(f'menu_{menu_uuid}')
    await redis.delete('menus')
    await delete_dish_by_id(dish_uuid)

    return {'status': True, 'detail': 'The dish has been deleted'}
