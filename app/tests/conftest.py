import asyncio
import time
from typing import Any, AsyncGenerator, Generator

import pytest
from async_asgi_testclient import TestClient
from src.database import get_redis


@pytest.fixture(scope='session')
def event_loop() -> Generator[asyncio.AbstractEventLoop, Any, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    pending = asyncio.all_tasks(loop)
    loop.run_until_complete(asyncio.gather(*pending))
    time.sleep(1)
    loop.close()


@pytest.fixture(scope='function')
async def client() -> AsyncGenerator[TestClient, None]:
    from src.main import app
    async with TestClient(app) as client:
        yield client


@pytest.fixture(scope='session')
async def redis():
    f = get_redis()
    redis = await f.asend(None)
    await redis.flushall()

    yield redis

    try:
        await f.asend(None)
    except StopAsyncIteration:
        pass


@pytest.fixture(scope='session', autouse=True)
async def clear_redis_cache():
    f = get_redis()
    redis = await f.asend(None)
    await redis.flushall()
    try:
        await f.asend(None)
    except StopAsyncIteration:
        pass
