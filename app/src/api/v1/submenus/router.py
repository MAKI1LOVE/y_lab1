from typing import Annotated
from uuid import UUID

from aioredis import Redis
from fastapi import APIRouter, Body, Depends, Path
from src.api.v1.submenus.schemas import NewSubmenu, SubmenuCount
from src.api.v1.submenus.service import (
    create_submenu_service,
    delete_submenu_service,
    get_submenu_service,
    get_submenus_service,
    patch_submenu_service,
)
from src.database import get_redis

submenus_router = APIRouter()


@submenus_router.get('', status_code=200, response_model=list[SubmenuCount])
async def get_submenus(
        menu_uuid: Annotated[UUID, Path()],
        redis: Annotated[Redis, Depends(get_redis)]
):
    return await get_submenus_service(redis, menu_uuid)


@submenus_router.post('', status_code=201, response_model=SubmenuCount)
async def create_submenu(
        menu_uuid: Annotated[UUID, Path()],
        new_submenu: Annotated[NewSubmenu, Body()],
        redis: Annotated[Redis, Depends(get_redis)],
):
    return await create_submenu_service(redis, menu_uuid, new_submenu)


@submenus_router.get('/{submenu_uuid}', status_code=200, response_model=SubmenuCount)
async def get_submenu(
        menu_uuid: Annotated[UUID, Path()],
        submenu_uuid: Annotated[UUID, Path()],
        redis: Annotated[Redis, Depends(get_redis)],
):
    return await get_submenu_service(redis, menu_uuid, submenu_uuid)


@submenus_router.patch('/{submenu_uuid}', status_code=200, response_model=SubmenuCount)
async def patch_submenu(
        menu_uuid: Annotated[UUID, Path()],
        submenu_uuid: Annotated[UUID, Path()],
        new_submenu: Annotated[NewSubmenu, Body()],
        redis: Annotated[Redis, Depends(get_redis)],
):
    return await patch_submenu_service(redis, menu_uuid, submenu_uuid, new_submenu)


@submenus_router.delete('/{submenu_uuid}', status_code=200, response_model=dict)
async def delete_submenu(
        menu_uuid: Annotated[UUID, Path()],
        submenu_uuid: Annotated[UUID, Path()],
        redis: Annotated[Redis, Depends(get_redis)],
):
    await delete_submenu_service(redis, menu_uuid, submenu_uuid)

    return {'status': True, 'detail': 'The submenu has been deleted'}
