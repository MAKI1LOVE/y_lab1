from fastapi import APIRouter

from src.api.v1.dishes.router import dishes_router
from src.api.v1.menus.router import menus_router
from src.api.v1.submenus.router import submenus_router

v1_router = APIRouter()

v1_router.include_router(menus_router, prefix='/menus')
v1_router.include_router(submenus_router, prefix='/menus/{menu_uuid}/submenus')
v1_router.include_router(dishes_router, prefix='/menus/{menu_uuid}/submenus/{submenu_uuid}/dishes')
