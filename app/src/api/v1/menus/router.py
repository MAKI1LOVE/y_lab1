from typing import Annotated
from uuid import UUID

from aioredis import Redis
from fastapi import APIRouter, Body, Depends, Path
from src.api.v1.menus.schemas import MenuWithCount, NewMenu
from src.api.v1.menus.service import (
    create_menu_service,
    delete_menu_service,
    get_all_menus_service,
    get_menu_service,
    get_menus_full_service,
    patch_menu_service,
)
from src.database import get_redis

menus_router = APIRouter()


@menus_router.get('/full', status_code=200, response_model=dict)
async def get_menus_full():
    menus = await get_menus_full_service()
    return {'menus': menus}


@menus_router.get('/{menu_uuid}', status_code=200, response_model=MenuWithCount)
async def get_menu(
        menu_uuid: Annotated[UUID, Path()],
        redis: Annotated[Redis, Depends(get_redis)],
):
    return await get_menu_service(redis, menu_uuid)


@menus_router.patch('/{menu_uuid}', status_code=200, response_model=MenuWithCount)
async def patch_menu(
        menu_uuid: Annotated[UUID, Path()],
        new_menu: Annotated[NewMenu, Body()],
        redis: Annotated[Redis, Depends(get_redis)]
):
    return await patch_menu_service(redis, menu_uuid, new_menu)


@menus_router.delete('/{menu_uuid}', status_code=200, response_model=dict)
async def delete_menu(
        menu_uuid: Annotated[UUID, Path()],
        redis: Annotated[Redis, Depends(get_redis)],
):
    await delete_menu_service(redis, menu_uuid)

    return {'status': True, 'detail': 'The menu has been deleted'}


@menus_router.get('', status_code=200, response_model=list[MenuWithCount])
async def get_menus(
        redis: Annotated[Redis, Depends(get_redis)],
):
    return await get_all_menus_service(redis)


@menus_router.post('', status_code=201, response_model=MenuWithCount)
async def create_menu(
        new_menu: Annotated[NewMenu, Body()],
        redis: Annotated[Redis, Depends(get_redis)],
):
    return await create_menu_service(redis, new_menu)
