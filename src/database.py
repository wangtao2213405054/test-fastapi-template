
from typing import Any, Type, TypeVar
from datetime import datetime

from fastapi.encoders import jsonable_encoder

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import Select, Insert, Update, MetaData
from sqlalchemy.exc import DatabaseError
from sqlmodel import SQLModel

from src.config import settings
from src.constants import DB_NAMING_CONVENTION
from src.exceptions import DatabaseConflictError, NotFound

T = TypeVar("T", bound=SQLModel)


# Mysql 数据库地址
DATABASE_URL = str(settings.DATABASE_URL)

engine = create_async_engine(DATABASE_URL, echo=settings.ENVIRONMENT.is_debug)
metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)

# 异步的数据库 session, 异步会话对象的工厂函数
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def catch_database_exceptions(func):
    """
    捕获 SQLAlchemy 抛出的 DatabaseError 并将结果转换成 JSON 返回
    :param func:
    :return:
    """
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return result
        except DatabaseError as error:
            error.orig = str(error.orig)
            raise DatabaseConflictError(jsonable_encoder(error))

    return wrapper


@catch_database_exceptions
async def fetch_one(sql: Select | Insert | Update) -> T | None:
    """
    处理数据库单条数据
    :param sql: SQLAlchemy 语句
    :return: 返回数据库信息或 None
    """
    async with async_session() as session:
        results = await session.execute(sql)
        return results.scalars().first()


@catch_database_exceptions
async def select_one(sql: Select) -> T:
    """
    查询单条数据, 如果未查询到则抛出 <NotFound> 异常
    :param sql: 查询语句
    :return:
    """
    async with async_session() as session:
        results = await session.execute(sql)
        data = results.scalars().first()
        if not data:
            raise NotFound()

        return data


@catch_database_exceptions
async def fetch_all(sql: Select | Insert | Update) -> list[T]:
    """
    处理数据库多条数据
    :param sql: SQLAlchemy 语句
    :return: 返回数据库信息列表
    """
    async with async_session() as session:
        results = await session.execute(sql)
        return [result for result in results.scalars().all()]


@catch_database_exceptions
async def execute(sql: Insert | Update) -> None:
    """
    执行数据库 SQLAlchemy 语句
    :param sql: SQLAlchemy 语句
    :return: 不返回任何信息
    """
    async with async_session() as session:
        await session.execute(sql)


@catch_database_exceptions
async def insert_one(table: Type[SQLModel], model: SQLModel) -> T:
    """
    向表中添加一个数据
    :param table: 要添加的模型表, 需要继承与 SQLModel 且 table = True
    :param model: 要添加的数据
    :return:
    """
    async with async_session() as session:
        data = table.model_validate(model)
        session.add(data)
        await session.commit()
        return data


@catch_database_exceptions
async def update_one(table: SQLModel) -> T:
    """
    向表中更新一条数据
    :param table: 要更新的数据模型
    :return: 返回更新后的数据模型
    """
    async with async_session() as session:

        if hasattr(table, "updateTime"):
            table.updateTime = datetime.now()

        session.add(table)
        await session.commit()
        await session.refresh(table)
        return table
