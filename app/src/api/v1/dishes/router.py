from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from src.api.v1.dishes.exceptions import dish_not_found
from src.api.v1.dishes.schemas import Dish, NewDish
from src.api.v1.dishes.service import (
    add_dish,
    delete_dish_by_id,
    get_all_dishes,
    get_dish_by_id,
    update_dish,
)

dishes_router = APIRouter()


@dishes_router.get('', status_code=200, response_model=list[Dish])
async def get_dishes(menu_uuid: UUID, submenu_uuid: UUID):
    dishes = await get_all_dishes(submenu_uuid)
    if dishes is None:
        return []

    return [Dish.model_validate(dish) for dish in dishes]


@dishes_router.post('', status_code=201, response_model=Dish)
async def create_dish(menu_uuid: UUID, submenu_uuid: UUID, new_dish: NewDish):
    dish = await add_dish(submenu_uuid, new_dish.title, new_dish.description, new_dish.price)
    if dish is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='smth bad'
        )

    return Dish.model_validate(dish)


@dishes_router.get('/{dish_uuid}', status_code=200, response_model=Dish)
async def get_dish(menu_uuid: UUID, submenu_uuid: UUID, dish_uuid: UUID):
    dish = await get_dish_by_id(dish_uuid)
    if dish is None:
        await dish_not_found()

    return Dish.model_validate(dish)


@dishes_router.patch('/{dish_uuid}', status_code=200, response_model=Dish)
async def patch_dish(menu_uuid: UUID, submenu_uuid: UUID, dish_uuid: UUID, new_dish: NewDish):
    dish = await update_dish(dish_uuid, new_dish.title, new_dish.description, new_dish.price)
    if dish is None:
        await dish_not_found()

    return Dish.model_validate(dish)


@dishes_router.delete('/{dish_uuid}', status_code=200)
async def delete_dish(menu_uuid: UUID, submenu_uuid: UUID, dish_uuid: UUID):
    await delete_dish_by_id(dish_uuid)

    return {'status': True, 'detail': 'The dish has been deleted'}
