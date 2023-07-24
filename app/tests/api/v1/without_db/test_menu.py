# TODO
import uuid
from unittest import mock

import pytest
from async_asgi_testclient.response import Response

from tests.factories import MenuFactory


@pytest.mark.asyncio
async def test_get_empty_menus(client):
    with mock.patch('src.api.v1.menus.router.get_all_menus', return_value=None):
        response: Response = await client.get('/api/v1/menus')

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_all_menus(client):
    with mock.patch('src.api.v1.menus.router.get_all_menus', return_value=[MenuFactory()]):
        response: Response = await client.get('/api/v1/menus')

    assert response.status_code == 200
    assert response.json()[0]['title'] != ''


@pytest.mark.asyncio
async def test_add_menu(client):
    data = {'title': 'menu1', 'description': 'desc1'}

    with mock.patch('src.api.v1.menus.router.add_menu',
                    return_value=MenuFactory(title=data['title'], description=data['description'])) as mock_add:
        response: Response = await client.post('/api/v1/menus/', json=data)

    assert response.status_code == 201
    resp_data = response.json()
    assert resp_data['title'] == data['title']
    assert resp_data['description'] == data['description']
    assert resp_data['submenus_count'] == 0
    assert resp_data['dishes_count'] == 0
    mock_add.assert_called_once_with(data['title'], data['description'])


@pytest.mark.asyncio
async def test_get_menu(client):
    menu_uuid = uuid.uuid4()

    # with mock.patch('src.api.v1.menus.dependencies.get_menu_by_id',
    #                 return_value=MenuFactory(menu_uuid=menu_uuid)) as mock_get_menu:
    response: Response = await client.get(f'/api/v1/menus/{menu_uuid}')

    assert response.status_code == 200
    # mock_get_menu.assert_called_once_with(menu_uuid)
    assert response.json()['id'] == menu_uuid


@pytest.mark.asyncio
async def test_get_nonexist_menu(client):
    menu_uuid = uuid.uuid4()

    with mock.patch('src.api.v1.menus.dependencies.get_menu_by_id', return_value=None) as mock_get_menu:
        response: Response = await client.get(f'/aoi/v1/menus/{menu_uuid}')

    assert response.status_code == 404
    assert response.json()['detail'] == 'menu not found'
