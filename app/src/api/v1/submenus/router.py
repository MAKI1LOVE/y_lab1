from typing import Annotated
from uuid import UUID

from aioredis import Redis
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from src.api.v1.submenus.exceptions import submenu_not_found
from src.api.v1.submenus.schemas import NewSubmenu, SubMenu
from src.api.v1.submenus.service import (
    add_submenu,
    delete_submenu_by_id,
    get_all_submenus,
    get_submenu_by_id,
    update_submenu,
)
from src.database import get_redis
from src.utils import delete_all_keys, get_db_data, set_key

submenus_router = APIRouter()


@submenus_router.get('', status_code=200, response_model=list[SubMenu])
async def get_submenus(
        menu_uuid: Annotated[UUID, Path()],
        redis: Annotated[Redis, Depends(get_redis)]
):
    submenus_stored = await get_db_data(redis, f'menu_{menu_uuid}_submenus', get_all_submenus, menu_uuid)
    if submenus_stored is None:
        return []

    submenus = [SubMenu.model_validate(submenu) for submenu in submenus_stored]
    await set_key(redis, f'menu_{menu_uuid}_submenus', submenus)

    return submenus


@submenus_router.post('', status_code=201, response_model=SubMenu)
async def create_submenu(
        menu_uuid: Annotated[UUID, Path()],
        new_submenu: Annotated[NewSubmenu, Body()],
        redis: Annotated[Redis, Depends(get_redis)],
):
    submenu_db = await add_submenu(menu_uuid, new_submenu.title, new_submenu.description)
    if submenu_db is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='smth bad'
        )

    submenu = SubMenu.model_validate(submenu_db)

    await set_key(redis, f'menu_{menu_uuid}_submenu_{submenu.id}', submenu)
    await redis.delete(f'menu_{menu_uuid}_submenus')
    await redis.delete(f'menu_{menu_uuid}')
    await redis.delete('menus')

    return submenu


@submenus_router.get('/{submenu_uuid}', status_code=200, response_model=SubMenu)
async def get_submenu(
        menu_uuid: Annotated[UUID, Path()],
        submenu_uuid: Annotated[UUID, Path()],
        redis: Annotated[Redis, Depends(get_redis)],
):
    submenu_stored = await get_db_data(redis, f'menu_{menu_uuid}_submenu_{submenu_uuid}', get_submenu_by_id,
                                       menu_uuid, submenu_uuid)
    if submenu_stored is None:
        await submenu_not_found()

    submenu = SubMenu.model_validate(submenu_stored)
    await set_key(redis, f'menu_{menu_uuid}_submenu_{submenu.id}', submenu)

    return submenu


@submenus_router.patch('/{submenu_uuid}', status_code=200, response_model=SubMenu)
async def patch_submenu(
        menu_uuid: Annotated[UUID, Path()],
        submenu_uuid: Annotated[UUID, Path()],
        new_submenu: Annotated[NewSubmenu, Body()],
        redis: Annotated[Redis, Depends(get_redis)],
):
    updated_submenu = await update_submenu(menu_uuid, submenu_uuid, new_submenu.title, new_submenu.description)
    if updated_submenu is None:
        await submenu_not_found()

    submenu_db = await get_submenu_by_id(menu_uuid, updated_submenu[0])
    submenu = SubMenu.model_validate(submenu_db)

    await set_key(redis, f'menu_{menu_uuid}_submenu_{submenu.id}', submenu)
    await redis.delete(f'menu_{menu_uuid}_submenus')

    return submenu


@submenus_router.delete('/{submenu_uuid}', status_code=200)
async def delete_submenu(
        menu_uuid: Annotated[UUID, Path()],
        submenu_uuid: Annotated[UUID, Path()],
        redis: Annotated[Redis, Depends(get_redis)],
):
    await delete_all_keys(redis, f'menu_{menu_uuid}_submenu_{submenu_uuid}')
    await redis.delete(f'menu_{menu_uuid}_submenus')
    await redis.delete(f'menu_{menu_uuid}')
    await redis.delete('menus')
    await delete_submenu_by_id(menu_uuid, submenu_uuid)

    return {'status': True, 'detail': 'The submenu has been deleted'}
