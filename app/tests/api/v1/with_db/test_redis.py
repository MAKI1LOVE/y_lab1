from aioredis import Redis
from async_asgi_testclient import TestClient
from async_asgi_testclient.response import Response
from src.dependencies import get_key


async def test_get_menu_from_redis(client: TestClient, redis: Redis):
    new_menu = {'title': 't1', 'description': 'd1'}

    response: Response = await client.post('/api/v1/menus', json=new_menu)
    assert response.status_code == 201
    id = response.json()['id']

    cache = await get_key(redis, f'menu_{id}')
    assert cache['id'] is not None
    assert cache['title'] == new_menu['title']
    assert cache['description'] == new_menu['description']
    assert cache['submenus_count'] == 0
    assert cache['dishes_count'] == 0


async def test_delete_menu_from_redis(client: TestClient, redis: Redis):
    new_menu = {'title': 't1', 'description': 'd1'}

    response: Response = await client.post('/api/v1/menus', json=new_menu)
    assert response.status_code == 201
    id = response.json()['id']

    response2: Response = await client.delete(f'/api/v1/menus/{id}')
    assert response2.status_code == 200

    cache = await get_key(redis, f'menu_{id}')
    assert cache is None

    response3: Response = await client.get(f'/api/v1/menus/{id}')
    assert response3.status_code == 404


async def test_get_submenu_from_redis(client: TestClient, redis: Redis):
    new_menu = {'title': 'menu', 'description': 'd menu'}
    new_submenu = {'title': 'submenu', 'description': 'd submenu'}

    response: Response = await client.post('/api/v1/menus', json=new_menu)
    assert response.status_code == 201
    menu_id = response.json()['id']

    response2: Response = await client.post(f'/api/v1/menus/{menu_id}/submenus', json=new_submenu)
    assert response2.status_code == 201
    submenu_id = response2.json()['id']

    cache = await get_key(redis, f'menu_{menu_id}_submenu_{submenu_id}')
    assert cache['menu_id'] == str(menu_id)
    assert cache['title'] == new_submenu['title']
    assert cache['description'] == new_submenu['description']
    assert cache['dishes_count'] == 0

    cache = await get_key(redis, f'menu_{menu_id}')
    assert cache is None


async def test_delete_submenu_from_redis(client: TestClient, redis: Redis):
    new_menu = {'title': 'menu', 'description': 'd menu'}
    new_submenu = {'title': 'submenu', 'description': 'd submenu'}

    response: Response = await client.post('/api/v1/menus', json=new_menu)
    assert response.status_code == 201
    menu_id = response.json()['id']

    response2: Response = await client.post(f'/api/v1/menus/{menu_id}/submenus', json=new_submenu)
    assert response2.status_code == 201
    submenu_id = response2.json()['id']

    response3: Response = await client.delete(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}')
    assert response3.status_code == 200

    cache = await get_key(redis, f'menu_{menu_id}_submenu_{submenu_id}')
    assert cache is None

    cache = await get_key(redis, f'menu_{menu_id}')
    assert cache is None


async def test_get_dish_from_redis(client: TestClient, redis: Redis):
    new_menu = {'title': 'menu', 'description': 'd menu'}
    new_submenu = {'title': 'new submenu', 'description': 'new d submenu'}
    new_dish = {'title': 'new dish', 'description': 'new d dish', 'price': '12.1234'}

    response: Response = await client.post('/api/v1/menus', json=new_menu)
    assert response.status_code == 201
    menu_id = response.json()['id']

    response2: Response = await client.post(f'/api/v1/menus/{menu_id}/submenus', json=new_submenu)
    assert response2.status_code == 201
    submenu_id = response2.json()['id']

    response3: Response = await client.post(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', json=new_dish)
    assert response3.status_code == 201
    dish_id = response3.json()['id']

    cache = await get_key(redis, f'menu_{menu_id}_submenu_{submenu_id}_dish_{dish_id}')
    assert cache['submenu_id'] == str(submenu_id)
    assert cache['title'] == new_dish['title']
    assert cache['description'] == new_dish['description']
    assert cache['price'][-3] == '.'

    cache = await get_key(redis, f'menu_{menu_id}')
    assert cache is None

    cache = await get_key(redis, f'menu_{menu_id}_submenu_{submenu_id}')
    assert cache is None


async def test_delete_dish_from_redis(client: TestClient, redis: Redis):
    new_menu = {'title': 'menu', 'description': 'd menu'}
    new_submenu = {'title': 'new submenu', 'description': 'new d submenu'}
    new_dish = {'title': 'new dish', 'description': 'new d dish', 'price': '12.1234'}

    response: Response = await client.post('/api/v1/menus', json=new_menu)
    assert response.status_code == 201
    menu_id = response.json()['id']

    response2: Response = await client.post(f'/api/v1/menus/{menu_id}/submenus', json=new_submenu)
    assert response2.status_code == 201
    submenu_id = response2.json()['id']

    response3: Response = await client.post(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', json=new_dish)
    assert response3.status_code == 201
    dish_id = response3.json()['id']

    response4: Response = await client.delete(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
    assert response4.status_code == 200

    cache = await get_key(redis, f'menu_{menu_id}_submenu_{submenu_id}_dish_{dish_id}')
    assert cache is None

    cache = await get_key(redis, f'menu_{menu_id}')
    assert cache is None

    cache = await get_key(redis, f'menu_{menu_id}_submenu_{submenu_id}')
    assert cache is None
