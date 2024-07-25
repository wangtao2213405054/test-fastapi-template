# _author: Coke
# _date: 2023/12/15 22:10

from typing import AsyncContextManager
from contextlib import asynccontextmanager

from fastapi import FastAPI

from redis.asyncio import Redis
import redis.asyncio as aioredis

from src.models.types import RedisData
from src.config import settings

# Redis
redis_client: Redis


@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncContextManager:
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
