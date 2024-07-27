# _author: Coke
# _date: 2024/7/26 17:25
# _description: 数据库操作相关函数

from typing import Type, TypeVar, Any, Callable, Union
from datetime import datetime
from pydantic import BaseModel
from functools import wraps

from fastapi.encoders import jsonable_encoder

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import Select, Insert, Update, MetaData, BinaryExpression
from sqlalchemy.exc import DatabaseError
from sqlmodel import SQLModel, col, select

from src.config import settings
from src.constants import DB_NAMING_CONVENTION
from src.exceptions import DatabaseConflictError, DatabaseNotFound, DatabaseUniqueError

T = TypeVar("T", bound=SQLModel)

# Mysql 数据库地址
DATABASE_URL = str(settings.DATABASE_URL)

engine = create_async_engine(DATABASE_URL, echo=settings.ENVIRONMENT.is_debug)
metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)

# 异步的数据库 session, 异步会话对象的工厂函数
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class UniqueDetails(BaseModel):
    """ 校验重复的实例 """
    message: str  # 如果重复所抛出的信息
    kwargsKey: str | None = None  # 数据库模型的实例


def unique_check(
        table: Type[SQLModel],
        *,
        func_key: str = None,
        model_key: str = None,
        **unique: Union[UniqueDetails, str]
) -> Callable[..., Any]:
    """
    检查数据在数据表中是否存在相同的数据, 此装饰器会在 FastAPI 校验参数之前执行...

    :param table: 模型表
    :param func_key: 入参过滤的唯一 Key, 如修改时, 需要忽略自身
    :param model_key: 数据库模型过滤的唯一 Key, 可不传递, 不传递取 request_key
    :param unique: <UniqueDetails> 对象, key 为要检查的模型表实例
            如果要校验 User 模型表中的 username 字段唯一, 以下是示例:
                unique_check(User, username=UniqueDetails(
                    message="账号必须唯一",
                    value:需要校验的字段, 如果可 Key 值相同可不传递
                ))

            对应关系为: **unique 的 Key 为 数据库模型实例
                kwargsKey 为 入参的实例 Key

            如果当数据模型的实例与 unique 的 key 相同时, 可传递 str 类型, 及重复所抛出的信息
            示例:
                unique_check(User, username="账号必须唯一")
    :return:
    """

    # 如果 response_key 不为真则取 request_key
    model_key = model_key or func_key

    def decorator(func: Callable[..., Any]):

        @wraps(func)
        async def wrapper(*args, **kwargs):
            """ 回调函数的入参信息 """

            # 执行唯一性检查
            for key, detail in unique.items():

                # 兼容性的处理, 支持 UniqueDetails or Str
                if issubclass(detail.__class__, UniqueDetails):
                    _key = detail.kwargsKey or key
                    message = detail.message
                else:
                    _key = key
                    message = detail

                value = kwargs.get(_key)
                clause = [getattr(table, key) == value]
                if func_key:
                    clause.append(getattr(table, model_key) != func_key)

                result = await fetch_one(select(table).where(*clause))
                if result:
                    raise DatabaseUniqueError(message)

            # 调用原始函数
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def catch_database_exceptions(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    捕获 SQLAlchemy 抛出的 DatabaseError 并将结果转换成 JSON 返回

    :param func: 回调函数
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


def like(*, field: Any, keyword: str) -> BinaryExpression[bool]:
    """
    关键字模糊查询

    :param field: 数据库模型的字段 or 列
    :param keyword: 关键字
    :return:
    """
    return col(field).like(f"%{keyword if keyword else ""}%")


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
async def select_one(sql: Select) -> T | None:
    """
    查询单条数据, 如果未查询到则抛出 <NotFound> 异常

    :param sql: 查询语句
    :return:
    """
    async with async_session() as session:
        results = await session.execute(sql)
        data = results.scalars().first()

        if not data:
            raise DatabaseNotFound()

        # noinspection PyTypeChecker
        return data


@catch_database_exceptions
async def fetch_page(sql: Select, page: int = 1, size: int = 20) -> list[T]:
    """
    查询多条数据并进行分页

    :param sql: 查询的 sql 语句
    :param page: 当前页
    :param size: 每页大小
    :return:
    """
    async with async_session() as session:
        results = await session.execute(sql.offset(0 if page <= 1 else page - 1).limit(size))
        return [result for result in results.scalars().all()]


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


@catch_database_exceptions
async def delete_one(sql: Select) -> T:
    """
    从表中删除一条数据

    :param sql: 查询条件的 SQL 语句
    :return:
    """
    async with async_session() as session:
        results = await session.execute(sql)
        data = results.scalars().first()
        if not data:
            raise DatabaseNotFound()

        await session.delete(data)
        await session.commit()

        # noinspection PyTypeChecker
        return data
