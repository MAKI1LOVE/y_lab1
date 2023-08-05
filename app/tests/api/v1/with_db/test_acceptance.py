from async_asgi_testclient import TestClient
from async_asgi_testclient.response import Response
from src.api.v1.dishes.schemas import Dish
from src.api.v1.menus.schemas import Menu
from src.api.v1.submenus.schemas import SubMenu


async def test_acceptance1(client: TestClient):
    new_menu = {'title': 't1', 'description': 'd1'}
    new_submenu1 = {'title': 'submenu1', 'description': 'submenu1 desc'}
    new_submenu2 = {'title': 'submenu2', 'description': 'submenu2 desc'}
    new_dish1 = {'title': 'dish1', 'description': 'new dish1', 'price': '12'}
    new_dish2 = {'title': 'dish2', 'description': 'new dish2', 'price': '13'}

    # menu
    response: Response = await client.post('/api/v1/menus', json=new_menu)

    assert response.status_code == 201
    db_menu = Menu(**response.json())
    assert db_menu.id is not None
    assert db_menu.dishes_count == 0
    assert db_menu.submenus_count == 0

    # submenus
    response2: Response = await client.post(f'/api/v1/menus/{db_menu.id}/submenus', json=new_submenu1)
    response3: Response = await client.post(f'/api/v1/menus/{db_menu.id}/submenus', json=new_submenu2)
    response4: Response = await client.get(f'/api/v1/menus/{db_menu.id}')

    assert response2.status_code == 201
    db_submenu1 = SubMenu(**response2.json())
    assert db_submenu1.id is not None
    assert db_submenu1.dishes_count == 0

    assert response2.status_code == 201
    db_submenu2 = SubMenu(**response3.json())
    assert db_submenu2.id is not None
    assert db_submenu2.dishes_count == 0

    assert response4.status_code == 200
    assert response4.json()['submenus_count'] == 2

    # dishes
    response5: Response = await client.post(f'/api/v1/menus/{db_menu.id}/submenus/{db_submenu1.id}/dishes',
                                            json=new_dish1)
    response6: Response = await client.post(f'/api/v1/menus/{db_menu.id}/submenus/{db_submenu1.id}/dishes',
                                            json=new_dish2)
    response7: Response = await client.get(f'/api/v1/menus/{db_menu.id}/submenus/{db_submenu1.id}')
    response8: Response = await client.get(f'/api/v1/menus/{db_menu.id}')

    assert response5.status_code == 201
    db_dish1 = Dish(**response5.json())
    assert db_dish1.id is not None

    assert response6.status_code == 201
    db_dish2 = Dish(**response6.json())
    assert db_dish2.id is not None

    assert response7.status_code == 200
    assert response7.json()['dishes_count'] == 2

    assert response8.status_code == 200
    assert response8.json()['dishes_count'] == 2

    # delete menu
    response9: Response = await client.delete(f'/api/v1/menus/{db_menu.id}')
    response10: Response = await client.get(f'/api/v1/menus/{db_menu.id}/submenus/{db_submenu1.id}')
    response11: Response = \
        await client.get(f'/api/v1/menus/{db_menu.id}/submenus/{db_submenu1.id}/dishes/{db_dish1.id}')

    assert response9.status_code == 200
    assert response10.status_code == 404
    assert response10.json()['detail'] == 'submenu not found'
    assert response11.status_code == 404
    assert response11.json()['detail'] == 'dish not found'
