from typing import Annotated
from uuid import UUID

from aioredis import Redis
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from src.api.v1.menus.exceptions import menu_not_found
from src.api.v1.menus.schemas import Menu, NewMenu
from src.api.v1.menus.service import (
    add_menu,
    delete_menu_by_id,
    get_all_menus,
    get_menu_by_id,
    update_menu,
)
from src.database import get_redis
from src.utils import delete_all_keys, get_db_data, set_key

menus_router = APIRouter()


@menus_router.get('', status_code=200, response_model=list[Menu])
async def get_menus(
        redis: Annotated[Redis, Depends(get_redis)]
):
    menus_stored = await get_db_data(redis, 'menus', get_all_menus)

    if menus_stored is None:
        return []

    menus = [Menu.model_validate(menu) for menu in menus_stored]
    await set_key(redis, 'menus', menus)

    return menus


@menus_router.post('', status_code=201, response_model=Menu)
async def create_menu(
        new_menu: Annotated[NewMenu, Body()],
        redis: Annotated[Redis, Depends(get_redis)],
):
    menu_db = await add_menu(new_menu.title, new_menu.description)
    if menu_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='smth bad'
        )

    menu = Menu.model_validate(menu_db)
    await set_key(redis, f'menu_{menu.id}', menu)
    await redis.delete('menus')

    return menu


@menus_router.get('/{menu_uuid}', status_code=200, response_model=Menu)
async def get_menu(
        menu_uuid: Annotated[UUID, Path()],
        redis: Annotated[Redis, Depends(get_redis)],
):
    menu_stored = await get_db_data(redis, f'menu_{menu_uuid}', get_menu_by_id, menu_uuid)

    if menu_stored is None:
        await menu_not_found()

    menu = Menu.model_validate(menu_stored)
    await set_key(redis, f'menu_{menu.id}', menu)
    return menu


@menus_router.patch('/{menu_uuid}', status_code=200, response_model=Menu)
async def patch_menu(
        menu_uuid: Annotated[UUID, Path()],
        new_menu: Annotated[NewMenu, Body()],
        redis: Annotated[Redis, Depends(get_redis)]
):
    updated_menu_id = await update_menu(menu_uuid, new_menu.title, new_menu.description)
    if updated_menu_id is None:
        await menu_not_found()

    menu_db = await get_menu_by_id(updated_menu_id[0])
    menu = Menu.model_validate(menu_db)

    await set_key(redis, f'menu_{menu.id}', menu)
    await redis.delete('menus')

    return menu


@menus_router.delete('/{menu_uuid}', status_code=200)
async def delete_menu(
        menu_uuid: Annotated[UUID, Path()],
        redis: Annotated[Redis, Depends(get_redis)],
):
    await delete_all_keys(redis, f'menu_{menu_uuid}')
    await redis.delete('menus')
    await delete_menu_by_id(menu_uuid)

    return {'status': True, 'detail': 'The menu has been deleted'}
