from typing import Annotated
from uuid import UUID

from aioredis import Redis
from fastapi import APIRouter, Body, Depends, Path
from src.api.v1.dishes.schemas import Dish, NewDish
from src.api.v1.dishes.service import (
    create_dish_service,
    delete_dish_service,
    get_all_dishes_service,
    get_dish_service,
    patch_dish_service,
)
from src.database import get_redis

dishes_router = APIRouter()


@dishes_router.get('', status_code=200, response_model=list[Dish])
async def get_dishes(
        menu_uuid: Annotated[UUID, Path()],
        submenu_uuid: Annotated[UUID, Path()],
        redis: Annotated[Redis, Depends(get_redis)],
):
    return await get_all_dishes_service(redis, menu_uuid, submenu_uuid)


@dishes_router.post('', status_code=201, response_model=Dish)
async def create_dish(
        menu_uuid: Annotated[UUID, Path()],
        submenu_uuid: Annotated[UUID, Path()],
        new_dish: Annotated[NewDish, Body()],
        redis: Annotated[Redis, Depends(get_redis)],
):
    return await create_dish_service(redis, menu_uuid, submenu_uuid, new_dish)


@dishes_router.get('/{dish_uuid}', status_code=200, response_model=Dish)
async def get_dish(
        menu_uuid: Annotated[UUID, Path()],
        submenu_uuid: Annotated[UUID, Path()],
        dish_uuid: Annotated[UUID, Path()],
        redis: Annotated[Redis, Depends(get_redis)],
):
    return await get_dish_service(redis, menu_uuid, submenu_uuid, dish_uuid)


@dishes_router.patch('/{dish_uuid}', status_code=200, response_model=Dish)
async def patch_dish(
        menu_uuid: Annotated[UUID, Path()],
        submenu_uuid: Annotated[UUID, Path()],
        dish_uuid: Annotated[UUID, Path()],
        new_dish: Annotated[NewDish, Body()],
        redis: Annotated[Redis, Depends(get_redis)],

):
    return await patch_dish_service(redis, menu_uuid, submenu_uuid, dish_uuid, new_dish)


@dishes_router.delete('/{dish_uuid}', status_code=200, response_model=dict)
async def delete_dish(
        menu_uuid: UUID,
        submenu_uuid: UUID,
        dish_uuid: UUID,
        redis: Annotated[Redis, Depends(get_redis)]
):
    await delete_dish_service(redis, menu_uuid, submenu_uuid, dish_uuid)

    return {'status': True, 'detail': 'The dish has been deleted'}
