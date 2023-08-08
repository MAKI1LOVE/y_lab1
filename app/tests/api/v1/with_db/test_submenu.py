import uuid

from async_asgi_testclient import TestClient
from async_asgi_testclient.response import Response
from src.api.v1.menus.crud import add_menu
from src.api.v1.submenus.crud import add_submenu


async def test_get_submenus_empty(client: TestClient):
    response: Response = await client.get(f'/api/v1/menus/{uuid.uuid4()}/submenus')

    assert response.status_code == 200
    assert response.json() == []


async def test_create_submenu(client: TestClient):
    new_menu = {'title': 'menu', 'description': 'd menu'}
    new_submenu = {'title': 'submenu', 'description': 'd submenu'}

    menu = await add_menu(new_menu['title'], new_menu['description'])
    response: Response = await client.post(f'/api/v1/menus/{menu.id}/submenus', json=new_submenu)

    assert response.status_code == 201
    out = response.json()
    assert out['menu_id'] == str(menu.id)
    assert out['title'] == new_submenu['title']
    assert out['description'] == new_submenu['description']
    assert out['dishes_count'] == 0


async def test_add_submenu_bad_params(client: TestClient):
    new_menu = {'title': 'menu', 'description': 'd menu'}
    new_submenu = {'title': 1, 'description': 'd submenu'}

    menu = await add_menu(new_menu['title'], new_menu['description'])
    response: Response = await client.post(f'/api/v1/menus/{menu.id}/submenus', json=new_submenu)

    assert response.status_code == 422


async def test_get_submenus(client: TestClient):
    new_menu = {'title': 'menu', 'description': 'd menu'}
    new_submenu1 = {'title': 'submenu1', 'description': 'd submenu'}
    new_submenu2 = {'title': 'submenu2', 'description': 'd submenu'}

    menu = await add_menu(new_menu['title'], new_menu['description'])
    await add_submenu(menu.id, new_submenu1['title'], new_submenu1['description'])
    await add_submenu(menu.id, new_submenu2['title'], new_submenu2['description'])
    response: Response = await client.get(f'/api/v1/menus/{menu.id}/submenus')

    assert response.status_code == 200
    out = response.json()
    assert len(out) == 2
    assert out[0]['title'] in (new_submenu1['title'], new_submenu2['title'])
    assert out[0]['dishes_count'] == 0


async def test_get_submenu_by_id(client: TestClient):
    new_menu = {'title': 'menu', 'description': 'd menu'}
    new_submenu = {'title': 'submenu', 'description': 'd submenu'}

    menu = await add_menu(new_menu['title'], new_menu['description'])
    submenu = await add_submenu(menu.id, new_submenu['title'], new_submenu['description'])
    response: Response = await client.get(f'/api/v1/menus/{menu.id}/submenus/{submenu.id}')

    assert response.status_code == 200
    out = response.json()
    assert out['menu_id'] == str(menu.id)
    assert out['title'] == new_submenu['title']
    assert out['dishes_count'] == 0


async def test_get_submenu_wrong_id(client: TestClient):
    response: Response = await client.get(f'/api/v1/menus/{uuid.uuid4()}/submenus/{uuid.uuid4()}')

    assert response.status_code == 404
    assert response.json()['detail'] == 'submenu not found'


async def test_update_submenu(client: TestClient):
    new_menu = {'title': 'menu', 'description': 'd menu'}
    old_submenu = {'title': 'submenu', 'description': 'd submenu'}
    new_submenu = {'title': 'new submenu', 'description': 'new d submenu'}

    menu = await add_menu(new_menu['title'], new_menu['description'])
    submenu = await add_submenu(menu.id, old_submenu['title'], old_submenu['description'])
    response: Response = await client.patch(f'/api/v1/menus/{menu.id}/submenus/{submenu.id}', json=new_submenu)

    assert response.status_code == 200
    assert response.json()['title'] == new_submenu['title']


async def test_update_submenu_invalid_uuid(client: TestClient):
    new_menu = {'title': 'menu', 'description': 'd menu'}
    new_submenu = {'title': 'new submenu', 'description': 'new d submenu'}

    menu = await add_menu(new_menu['title'], new_menu['description'])
    response: Response = await client.patch(f'/api/v1/menus/{menu.id}/submenus/{uuid.uuid4()}', json=new_submenu)

    assert response.status_code == 404
    assert response.json()['detail'] == 'submenu not found'


async def test_delete_submenu(client: TestClient):
    new_menu = {'title': 'menu', 'description': 'd menu'}
    new_submenu = {'title': 'new submenu', 'description': 'new d submenu'}

    menu = await add_menu(new_menu['title'], new_menu['description'])
    submenu = await add_submenu(menu.id, new_submenu['title'], new_submenu['description'])
    response: Response = await client.delete(f'/api/v1/menus/{menu.id}/submenus/{submenu.id}')

    assert response.status_code == 200
    out = response.json()
    assert out['detail'] == 'The submenu has been deleted'
    assert out['status']


async def test_delete_submenu_invalid_uuid(client: TestClient):
    response: Response = await client.delete(f'/api/v1/menus/{uuid.uuid4()}/submenus/{uuid.uuid4()}')

    assert response.status_code == 200
    out = response.json()
    assert out['detail'] == 'The submenu has been deleted'
    assert out['status']
