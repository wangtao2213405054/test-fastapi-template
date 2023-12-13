
from typing import Any, AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import Select, Insert, Update, MetaData

from redis.asyncio import Redis
import redis.asyncio as aioredis

from src.config import settings
from src.constants import DB_NAMING_CONVENTION
from src.schemas import RedisData

# Mysql 数据库地址
DATABASE_URL = str(settings.DATABASE_URL)

engine = create_async_engine(DATABASE_URL)
metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)

# Redis
redis_client: Redis


# 异步的数据库 session, 异步会话对象的工厂函数
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def fetch_one(sql: Select | Insert | Update) -> dict[str, Any] | None:
    """
    处理数据库单条数据
    :param sql: SQLAlchemy 语句
    :return: 返回数据库信息或 None
    """
    async with async_session() as session:
        results = await session.execute(sql)
        return results.scalars().first()


async def fetch_all(sql: Select | Insert | Update) -> list[dict[str, Any]]:
    """
    处理数据库多条数据
    :param sql: SQLAlchemy 语句
    :return: 返回数据库信息列表
    """
    async with async_session() as session:
        results = await session.execute(sql)
        return [result for result in results.scalars().all()]


async def execute(sql: Insert | Update) -> None:
    """
    执行数据库 SQLAlchemy 语句
    :param sql: SQLAlchemy 语句
    :return: 不返回任何信息
    """
    async with async_session() as session:
        await session.execute(sql)


@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncGenerator:
    """
    FastAPI 启动时挂载 Redis 停止时释放 Redis
    :param _application: FastAPI 应用
    :return:
    """
    # 挂载
    pool = aioredis.ConnectionPool.from_url(
        str(settings.REDIS_URL), max_connections=10, decode_responses=True
    )
    global redis_client
    redis_client = aioredis.Redis(connection_pool=pool)

    yield

    if settings.ENVIRONMENT.is_testing:
        return
    # 释放
    await pool.disconnect()


async def set_redis_key(redis_data: RedisData, *, is_transaction: bool = False) -> None:
    """
    在 Redis 中设置键值对
    :param redis_data: 要设置的数据 <RedisData>
    :param is_transaction: 是否使用 Redis 的事务功能
    :return:
    """
    async with redis_client.pipeline(transaction=is_transaction) as pipe:
        await pipe.set(redis_data.key, redis_data.value)
        if redis_data.ttl:
            await pipe.expire(redis_data.key, redis_data.ttl)

        await pipe.execute()


async def get_by_key(key: str) -> str | None:
    """
    通过 key 获取 Redis 数据
    :param key: 要获取数据的 Key
    :return:
    """
    return await redis_client.get(key)


async def delete_by_key(key: str) -> None:
    """
    通过 Key 删除 Redis 的数据
    :param key: 要删除数据的 Key
    :return:
    """
    return await redis_client.delete(key)
