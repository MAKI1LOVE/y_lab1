import asyncio
from typing import Any, AsyncGenerator, Generator

import pytest
from async_asgi_testclient import TestClient


@pytest.fixture(scope='session')
def event_loop() -> Generator[asyncio.AbstractEventLoop, Any, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='function')
async def client() -> AsyncGenerator[TestClient, None]:
    from src.main import app
    async with TestClient(app) as client:
        yield client
