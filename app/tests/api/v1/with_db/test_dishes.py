import uuid

import pytest
from async_asgi_testclient.response import Response

from src.api.v1.dishes.service import add_dish
from src.api.v1.menus.service import add_menu
from src.api.v1.submenus.service import add_submenu


@pytest.mark.asyncio
async def test_get_dishes_empty(client):
    new_menu = {'title': 'menu', 'description': 'd menu'}
    new_submenu = {'title': 'new submenu', 'description': 'new d submenu'}

    menu = await add_menu(new_menu['title'], new_menu['description'])
    submenu = await add_submenu(menu.id, new_submenu['title'], new_submenu['description'])
    response: Response = await client.get(f'/api/v1/menus/{menu.id}/submenus/{submenu.id}/dishes')

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_add_dish(client):
    new_menu = {'title': 'menu', 'description': 'd menu'}
    new_submenu = {'title': 'new submenu', 'description': 'new d submenu'}
    new_dish = {'title': 'new dish', 'description': 'new d dish', 'price': '12.1234'}

    menu = await add_menu(new_menu['title'], new_menu['description'])
    submenu = await add_submenu(menu.id, new_submenu['title'], new_submenu['description'])
    response: Response = await client.post(f'/api/v1/menus/{menu.id}/submenus/{submenu.id}/dishes', json=new_dish)

    assert response.status_code == 201
    out = response.json()
    assert out['submenu_id'] == str(submenu.id)
    assert out['title'] == new_dish['title']
    assert out['description'] == new_dish['description']
    assert out['price'][-3] == '.'


@pytest.mark.asyncio
async def test_get_dishes(client):
    new_menu = {'title': 'menu', 'description': 'd menu'}
    new_submenu = {'title': 'new submenu', 'description': 'new d submenu'}
    new_dish1 = {'title': 'new dish1', 'description': 'new d dish1', 'price': '12'}
    new_dish2 = {'title': 'new dish2', 'description': 'new d dish2', 'price': '13'}

    menu = await add_menu(new_menu['title'], new_menu['description'])
    submenu = await add_submenu(menu.id, new_submenu['title'], new_submenu['description'])
    dish1 = await add_dish(submenu.id, new_dish1['title'], new_dish1['description'], new_dish1['price'])
    dish2 = await add_dish(submenu.id, new_dish1['title'], new_dish1['description'], new_dish1['price'])
    response: Response = await client.get(f'/api/v1/menus/{menu.id}/submenus/{submenu.id}/dishes')

    assert response.status_code == 200
    out = response.json()
    assert len(out) == 2
    assert out[0]['title'] in (new_dish1['title'], new_dish2['title'])


@pytest.mark.asyncio
async def test_get_dish_by_id(client):
    new_menu = {'title': 'menu', 'description': 'd menu'}
    new_submenu = {'title': 'new submenu', 'description': 'new d submenu'}
    new_dish = {'title': 'new dish', 'description': 'new d dish', 'price': '12'}

    menu = await add_menu(new_menu['title'], new_menu['description'])
    submenu = await add_submenu(menu.id, new_submenu['title'], new_submenu['description'])
    dish = await add_dish(submenu.id, new_dish['title'], new_dish['description'], new_dish['price'])
    response: Response = await client.get(f'/api/v1/menus/{menu.id}/submenus/{submenu.id}/dishes/{dish.id}')

    assert response.status_code == 200
    out = response.json()
    assert out['submenu_id'] == str(submenu.id)
    assert out['title'] == new_dish['title']
    assert out['description'] == new_dish['description']
    assert out['price'] == '12.00'


@pytest.mark.asyncio
async def test_get_dish_by_invalid_id(client):
    response: Response = await client.get(f'/api/v1/menus/{uuid.uuid4()}/submenus/{uuid.uuid4()}/dishes/{uuid.uuid4()}')

    assert response.status_code == 404
    assert response.json()['detail'] == 'dish not found'


@pytest.mark.asyncio
async def test_patch_dish(client):
    new_menu = {'title': 'menu', 'description': 'd menu'}
    new_submenu = {'title': 'new submenu', 'description': 'new d submenu'}
    old_dish = {'title': 'old dish', 'description': 'old d dish', 'price': '12'}
    new_dish = {'title': 'new dish', 'description': 'new d dish', 'price': '0'}

    menu = await add_menu(new_menu['title'], new_menu['description'])
    submenu = await add_submenu(menu.id, new_submenu['title'], new_submenu['description'])
    dish = await add_dish(submenu.id, old_dish['title'], old_dish['description'], old_dish['price'])
    response: Response = await client.patch(f'/api/v1/menus/{menu.id}/submenus/{submenu.id}/dishes/{dish.id}',
                                            json=new_dish)

    assert response.status_code == 200
    out = response.json()
    assert out['submenu_id'] == str(submenu.id)
    assert out['title'] == new_dish['title']
    assert out['description'] == new_dish['description']
    assert out['price'] == '0.00'


@pytest.mark.asyncio
async def test_patch_dish_invalid_id(client):
    new_dish = {'title': 'new dish', 'description': 'new d dish', 'price': '0'}

    response: Response = await client.patch(
        f'/api/v1/menus/{uuid.uuid4()}/submenus/{uuid.uuid4()}/dishes/{uuid.uuid4()}',
        json=new_dish)

    assert response.status_code == 404
    assert response.json()['detail'] == 'dish not found'


@pytest.mark.ascyno
async def test_delete_dish(client):
    new_menu = {'title': 'menu', 'description': 'd menu'}
    new_submenu = {'title': 'new submenu', 'description': 'new d submenu'}
    new_dish = {'title': 'new dish', 'description': 'new d dish', 'price': '12'}

    menu = await add_menu(new_menu['title'], new_menu['description'])
    submenu = await add_submenu(menu.id, new_submenu['title'], new_submenu['description'])
    dish = await add_dish(submenu.id, new_dish['title'], new_dish['description'], new_dish['price'])
    response: Response = await client.delete(f'/api/v1/menus/{menu.id}/submenus/{submenu.id}/dishes/{dish.id}')

    assert response.status_code == 200
    out = response.json()
    assert out['status']
    assert out['detail'] == 'The dish has been deleted'


@pytest.mark.ascyno
async def test_delete_dish_invalid_uuid(client):
    response: Response = \
        await client.delete(f'/api/v1/menus/{uuid.uuid4()}/submenus/{uuid.uuid4()}/dishes/{uuid.uuid4()}')

    assert response.status_code == 200
    out = response.json()
    assert out['status']
    assert out['detail'] == 'The dish has been deleted'
