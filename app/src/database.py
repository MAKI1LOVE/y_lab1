import contextlib
from collections.abc import AsyncGenerator

import aioredis
from aioredis import Redis
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from src.config import settings

engine: AsyncEngine = create_async_engine(settings.DB_URL, echo=False)
session_maker: async_sessionmaker = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(
    DeclarativeBase,
):
    pass


async def init_db():
    global engine, session_maker

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    redis = await aioredis.from_url(settings.REDIS_URL)
    await redis.flushall()
    await redis.close()


@contextlib.asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_maker.begin() as session:
        yield session


async def get_redis() -> AsyncGenerator[Redis, None]:
    redis = await aioredis.from_url(settings.REDIS_URL)
    yield redis
    await redis.close()
