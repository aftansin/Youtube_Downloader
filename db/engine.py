from typing import Union

from sqlalchemy import URL, MetaData
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine


def get_async_engine(url: Union[URL, str]):
    return create_async_engine(url=url, echo=False, pool_pre_ping=True)


def get_session_maker(engine: AsyncEngine):
    return async_sessionmaker(engine, expire_on_commit=False)


async def update_schemas(engine: AsyncEngine, metadata: MetaData):
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
