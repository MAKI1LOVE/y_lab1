import uuid

from async_asgi_testclient import TestClient
from async_asgi_testclient.response import Response
from src.api.v1.dishes.crud import add_dish
from src.api.v1.menus.crud import add_menu
from src.api.v1.submenus.crud import add_submenu


async def test_get_menus_empty(client: TestClient):
    response: Response = await client.get('/api/v1/menus')

    assert response.status_code == 200
    assert response.json() == []


async def test_get_menus(client: TestClient):
    new_menu1 = {'title': 't1', 'description': 'd1'}
    new_menu2 = {'title': 't2', 'description': 'd2'}

    await add_menu(new_menu1['title'], new_menu1['description'])
    await add_menu(new_menu2['title'], new_menu2['description'])
    response: Response = await client.get('/api/v1/menus')

    assert response.status_code == 200
    out = response.json()
    assert len(out) == 2


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


# @pytest.mark.skip
async def test_get_menus_full(client: TestClient):
    new_menu = {'title': 'menu1', 'description': 'menu1 desc'}
    new_submenu1 = {'title': 'submenu1', 'description': 'submenu1 desc'}
    new_submenu2 = {'title': 'submenu2', 'description': 'submenu2 desc'}
    new_dish1 = {'title': 'dish1', 'description': 'new dish1', 'price': '12'}
    new_dish2 = {'title': 'dish2', 'description': 'new dish2', 'price': '13'}

    menu_db = await add_menu(new_menu['title'], new_menu['description'])
    submenu1_db = await add_submenu(menu_db.id, new_submenu1['title'], new_submenu1['description'])
    submenu2_db = await add_submenu(menu_db.id, new_submenu2['title'], new_submenu2['description'])
    dish1_db = await add_dish(submenu1_db.id, new_dish1['title'], new_dish1['description'], new_dish1['price'])
    dish2_db = await add_dish(submenu1_db.id, new_dish2['title'], new_dish2['description'], new_dish2['price'])

    response: Response = await client.get('/api/v1/menus/full')

    assert response.status_code == 200
    menus = response.json().get('menus')
    assert menus is not None
    assert menus[0]['id'] == str(menu_db.id)
    assert menus[0]['submenus'][0]['id'] == str(submenu1_db.id)
    assert menus[0]['submenus'][0]['dishes'][0]['id'] == str(dish1_db.id)
    assert menus[0]['submenus'][0]['dishes'][1]['id'] == str(dish2_db.id)
    assert menus[0]['submenus'][1]['id'] == str(submenu2_db.id)
    assert menus[0]['submenus'][1]['dishes'] == []
