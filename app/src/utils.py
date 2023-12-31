import asyncio
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Annotated, Any

from aioredis import Redis
from asyncpg.pgproto.pgproto import UUID as PG_UUID
from fastapi import Depends
from orjson import orjson
from pydantic import BaseModel
from src.database import get_redis, get_session


def get_session_deco(func: Callable) -> Any:
    """
    Give new session for every request in service.
    No need to create dependency in endpoint functions.
    :param func: func to wrap
    :return: simple data transfer
    """

    async def wrapper(*args, **kwargs) -> Any:
        async with get_session() as session:
            data = await func(*args, **kwargs, session=session)
            await session.commit()

        return data

    return wrapper


def orjson_custom_data_decoder(obj: Any) -> Any:
    if isinstance(obj, PG_UUID):
        return uuid.UUID(str(obj), version=4)

    if isinstance(obj, BaseModel):
        return dict(obj)


async def set_key(
        redis: Redis,
        key: str,
        data: Any,
        secs_to_expire: int = 3600
) -> None:
    data = {'data': data, 'expires': time.time() + secs_to_expire}
    value = orjson.dumps(data, default=orjson_custom_data_decoder)
    await redis.set(key, value)


async def get_key(redis: Redis, key: str) -> Any:
    value = await redis.get(key)
    if value is None:
        return None

    value = orjson.loads(value)
    if value.get('expires') < time.time():
        await redis.unlink(key)
        return None

    return value.get('data')


async def delete_all_keys(redis: Redis, start_key: str) -> None:
    start_key = f'{start_key}*'
    keys = await redis.keys(start_key)
    await asyncio.gather(*[redis.delete(key) for key in keys])


async def get_cache_data(
        redis: Annotated[Redis, Depends(get_redis)],
        key: str,
) -> Any:
    return await get_key(redis, key)


async def get_db_data(
        redis: Redis,
        key: str,
        func: Callable[[Any], Awaitable[Any]],
        *args,
        **kwargs,
) -> Any:
    cache = await get_cache_data(redis, key)
    if cache is not None:
        return cache

    return await func(*args, **kwargs)
