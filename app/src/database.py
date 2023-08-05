import contextlib
import uuid
from typing import AsyncGenerator

from sqlalchemy import Column, ForeignKey, MetaData, String, Table, Uuid
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from src.config import settings

engine: AsyncEngine
session_maker: async_sessionmaker

metadata = MetaData()


async def init_db():
    global engine, session_maker
    engine = create_async_engine(settings.DB_URL, echo=False)
    session_maker = async_sessionmaker(bind=engine, expire_on_commit=True)

    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)

    print('connected')


@contextlib.asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_maker.begin() as session:
        yield session


menus_table = Table(
    'menus',
    metadata,
    Column('id', Uuid, primary_key=True, default=uuid.uuid4),
    Column('title', String, nullable=False),
    Column('description', String, nullable=False),

)

submenus_table = Table(
    'submenus',
    metadata,
    Column('id', Uuid, primary_key=True, nullable=False, default=uuid.uuid4),
    Column('menu_id', Uuid, ForeignKey('menus.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False),
    Column('title', String, nullable=False),
    Column('description', String, nullable=False)
)

dishes_table = Table(
    'dishes',
    metadata,
    Column('id', Uuid, primary_key=True, nullable=False, default=uuid.uuid4),
    Column('submenu_id', Uuid, ForeignKey('submenus.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False),
    Column('title', String, nullable=False),
    Column('description', String, nullable=False),
    Column('price', String, nullable=False)
)
