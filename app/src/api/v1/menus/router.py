from uuid import UUID

from fastapi import APIRouter, Body, HTTPException, Path, status
from src.api.v1.menus.exceptions import menu_not_found
from src.api.v1.menus.schemas import Menu, NewMenu
from src.api.v1.menus.service import (
    add_menu,
    delete_menu_by_id,
    get_all_menus,
    get_menu_by_id,
    update_menu,
)

menus_router = APIRouter()


@menus_router.get('', status_code=200, response_model=list[Menu])
async def get_menus():
    menus = await get_all_menus()
    if menus is None:
        return []

    return [Menu.model_validate(menu) for menu in menus]


@menus_router.post('', status_code=201, response_model=Menu)
async def create_menu(new_menu: NewMenu = Body()):
    menu = await add_menu(new_menu.title, new_menu.description)
    if menu is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='smth bad'
        )

    return Menu.model_validate(menu)


@menus_router.get('/{menu_uuid}', status_code=200, response_model=Menu)
async def get_menu(menu_uuid: UUID = Path()):
    menu = await get_menu_by_id(menu_uuid)
    if menu is None:
        await menu_not_found()

    return Menu.model_validate(menu)


@menus_router.patch('/{menu_uuid}', status_code=200, response_model=Menu)
async def patch_menu(menu_uuid: UUID = Path(), new_menu: NewMenu = Body()):
    updated_menu_id = await update_menu(menu_uuid, new_menu.title, new_menu.description)
    if updated_menu_id is None:
        await menu_not_found()

    return await get_menu_by_id(updated_menu_id[0])


@menus_router.delete('/{menu_uuid}', status_code=200)
async def delete_menu(menu_uuid: UUID = Path()):
    await delete_menu_by_id(menu_uuid)

    return {'status': True, 'detail': 'The menu has been deleted'}
