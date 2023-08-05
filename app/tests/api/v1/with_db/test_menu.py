import uuid

from async_asgi_testclient import TestClient
from async_asgi_testclient.response import Response
from src.api.v1.menus.service import add_menu


async def test_get_menus_empty(client: TestClient):
    response: Response = await client.get('/api/v1/menus')

    assert response.status_code == 200
    assert response.json() == []


async def test_create_menu(client: TestClient):
    new_menu = {'title': 't1', 'description': 'd1'}

    response: Response = await client.post('/api/v1/menus', json=new_menu)

    assert response.status_code == 201
    out = response.json()
    assert out['id'] is not None
    assert out['title'] == new_menu['title']
    assert out['description'] == new_menu['description']
    assert out['submenus_count'] == 0
    assert out['dishes_count'] == 0


async def test_create_menu_bad_fields(client: TestClient):
    new_menu = {'titlee': 't', 'description': 1}

    response: Response = await client.post('/api/v1/menus', json=new_menu)

    assert response.status_code == 422


async def test_get_menu(client: TestClient):
    new_menu = {'title': 't1', 'description': 'd1'}

    menu = await add_menu(new_menu['title'], new_menu['description'])
    response: Response = await client.get(f'/api/v1/menus/{menu.id}')

    assert response.status_code == 200
    out = response.json()
    assert out['id'] == str(menu.id)
    assert out['title'] == new_menu['title']
    assert out['description'] == new_menu['description']
    assert out['submenus_count'] == 0
    assert out['dishes_count'] == 0


async def test_get_menu_wrong_uuid(client: TestClient):
    wrong_uuid = uuid.uuid4()

    response: Response = await client.get(f'/api/v1/menus/{wrong_uuid}')

    assert response.status_code == 404
    assert response.json()['detail'] == 'menu not found'


async def test_get_menu_wrong_uuid_format(client: TestClient):
    response: Response = await client.get('/api/v1/menus/1')

    assert response.status_code == 422


async def test_get_menus(client: TestClient):
    new_menu1 = {'title': 't1', 'description': 'd1'}
    new_menu2 = {'title': 't2', 'description': 'd2'}

    await add_menu(new_menu1['title'], new_menu1['description'])
    await add_menu(new_menu2['title'], new_menu2['description'])
    response: Response = await client.get('/api/v1/menus')

    assert response.status_code == 200
    out = response.json()
    assert len(out) == 2


async def test_patch_menu(client: TestClient):
    old_menu = {'title': 't_old', 'description': 'd_old'}
    new_menu = {'title': 't_new', 'description': 'd_new'}

    menu = await add_menu(old_menu['title'], old_menu['description'])
    response: Response = await client.patch(f'/api/v1/menus/{menu.id}', json=new_menu)

    assert response.status_code == 200
    out = response.json()
    assert out['title'] == new_menu['title']
    assert out['description'] == new_menu['description']


async def test_patch_wrong_uuid(client: TestClient):
    new_menu = {'title': 't_new', 'description': 'd_new'}

    response: Response = await client.patch(f'/api/v1/menus/{uuid.uuid4()}', json=new_menu)

    assert response.status_code == 404
    assert response.json()['detail'] == 'menu not found'


async def test_delete_menu(client: TestClient):
    new_menu = {'title': 't1', 'description': 'd1'}

    menu = await add_menu(new_menu['title'], new_menu['description'])
    response: Response = await client.delete(f'/api/v1/menus/{menu.id}')

    assert response.status_code == 200
    out = response.json()
    assert out['status']
    assert out['detail'] == 'The menu has been deleted'


async def test_delete_menu_wrong_uuid(client: TestClient):
    response: Response = await client.delete(f'/api/v1/menus/{uuid.uuid4()}')

    assert response.status_code == 200
    out = response.json()
    assert out['status']
    assert out['detail'] == 'The menu has been deleted'
