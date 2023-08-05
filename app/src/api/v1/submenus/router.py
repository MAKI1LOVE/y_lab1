from uuid import UUID

from fastapi import APIRouter, Body, HTTPException, Path, status
from src.api.v1.submenus.exceptions import submenu_not_found
from src.api.v1.submenus.schemas import NewSubmenu, SubMenu
from src.api.v1.submenus.service import (
    add_submenu,
    delete_submenu_by_id,
    get_all_submenus,
    get_submenu_by_id,
    update_submenu,
)

submenus_router = APIRouter()


@submenus_router.get('', status_code=200, response_model=list[SubMenu])
async def get_submenus(menu_uuid: UUID = Path()):
    submenus = await get_all_submenus(menu_uuid)
    if submenus is None:
        return []

    return [SubMenu.model_validate(submenu) for submenu in submenus]


@submenus_router.post('', status_code=201, response_model=SubMenu)
async def create_submenu(menu_uuid: UUID = Path(), new_submenu: NewSubmenu = Body()):
    submenu = await add_submenu(menu_uuid, new_submenu.title, new_submenu.description)
    if submenu is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='smth bad'
        )

    return SubMenu.model_validate(submenu)


@submenus_router.get('/{submenu_uuid}', status_code=200, response_model=SubMenu)
async def get_submenu(menu_uuid: UUID = Path(), submenu_uuid: UUID = Path()):
    submenu = await get_submenu_by_id(menu_uuid, submenu_uuid)
    if submenu is None:
        await submenu_not_found()

    return SubMenu.model_validate(submenu)


@submenus_router.patch('/{submenu_uuid}', status_code=200, response_model=SubMenu)
async def patch_submenu(
        menu_uuid: UUID = Path(),
        submenu_uuid: UUID = Path(),
        new_submenu: NewSubmenu = Body()
):
    updated_submenu = await update_submenu(menu_uuid, submenu_uuid, new_submenu.title, new_submenu.description)
    if updated_submenu is None:
        await submenu_not_found()

    submenu = await get_submenu_by_id(menu_uuid, updated_submenu[0])

    return SubMenu.model_validate(submenu)


@submenus_router.delete('/{submenu_uuid}', status_code=200)
async def delete_submenu(menu_uuid: UUID = Path(), submenu_uuid: UUID = Path()):
    await delete_submenu_by_id(menu_uuid, submenu_uuid)

    return {'status': True, 'detail': 'The submenu has been deleted'}
