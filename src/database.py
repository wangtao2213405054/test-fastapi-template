# _author: Coke
# _date: 2024/7/26 17:25
# _description: 数据库操作相关函数

import asyncio
from datetime import datetime
from functools import wraps
from typing import Any, Awaitable, Callable, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import BinaryExpression, MetaData
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import col
from sqlmodel import select as _select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import Select, SelectOfScalar

from src.config import settings
from src.constants import DB_NAMING_CONVENTION
from src.exceptions import DatabaseNotFound, DatabaseUniqueError

_TSelectParam = TypeVar("_TSelectParam", bound=Any)


# Mysql 数据库地址
DATABASE_URL = str(settings.DATABASE_URL)

engine = create_async_engine(DATABASE_URL, echo=settings.ENVIRONMENT.is_debug)
metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)

# 异步的数据库 session, 异步会话对象的工厂函数
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def get_session() -> AsyncSession:
    """
    返回异步数据库会话对象

    :return:
    """
    return async_session()


class UniqueDetails(BaseModel):
    """校验重复的实例"""

    message: str  # 如果重复所抛出的信息
    kwargsKey: str | None = None  # 数据库模型的实例


def unique_check(
    table: Type[_TSelectParam],
    *,
    func_key: str | None = None,
    model_key: str | None = None,
    **unique: UniqueDetails | str,
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
    model_key = model_key or func_key  # type: ignore

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Callable[..., Any]:  # type: ignore
            """回调函数的入参信息"""

            message_list: list[str] = []
            tasks: list[Awaitable] = []

            # 执行唯一性检查
            for key, detail in unique.items():
                # 兼容性的处理, 支持 UniqueDetails or Str
                if issubclass(detail.__class__, UniqueDetails):
                    _key = detail.kwargsKey or key
                    message = detail.message

                else:
                    _key = key
                    message = detail

                message_list.append(message)
                clause = [getattr(table, key) == kwargs.get(_key)]

                # 只有当调用此装饰器的函数Key 为真时才添加此条件
                if func_key and kwargs.get("func_key"):
                    clause.append(getattr(table, model_key) != kwargs.get("func_key"))  # type: ignore

                tasks.append(select(_select(table).where(*clause), nullable=True))

            task_result = await asyncio.gather(*tasks)

            error_message = []

            for message, result in zip(message_list, task_result):
                if result:
                    error_message.append(message)

            if len(error_message):
                raise DatabaseUniqueError(f"{"、".join(error_message)}已存在")

            # 调用原始函数
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def like(*, field: Any, keyword: str) -> BinaryExpression[bool]:
    """
    关键字模糊查询

    :param field: 数据库模型的字段 or 列
    :param keyword: 关键字
    :return:
    """
    return col(field).like(f"%{keyword if keyword else ""}%")


def joined_load(*args: Any, **kwargs: Any) -> Any:
    """
    使用 SQL 的 JOIN 语句来一次性加载父对象和相关联的子对象。

    它会通过 JOIN 操作将父对象和子对象的数据结合在一起，从而减少了对数据库的访问次数。

    - 对于一对多和多对多关系，joined load 可以非常高效，因为它通过一个查询返回所有必要的数据。
    - 当子对象数量非常大时，joined load 可能会导致查询结果的行数膨胀。

    :param args:
    :param kwargs:
    :return:
    """
    return joinedload(*args, **kwargs)


def select_in_load(*args: Any, recursion_depth: int | None = None) -> Any:
    """
    select in load 使用多个查询来加载父对象和相关联的子对象。

    首先会执行一个查询来获取所有父对象，然后再执行另一个查询来获取所有相关的子对象。
    这种方法会执行两个独立的查询，而不是一个复杂的 JOIN 查询。

    - select in load 对于一对多和多对多关系，尤其是在子对象数量很大的情况下，
        可能比 joined load 更高效，因为它避免了大结果集的问题。

    - 它通常会生成较少的总结果行数，但会增加额外的查询。

    :param args:
    :param recursion_depth:
    :return:
    """
    return selectinload(*args, recursion_depth=recursion_depth)


async def select(
    statement: Select[_TSelectParam] | SelectOfScalar[_TSelectParam],
    *,
    nullable: bool = False,
) -> _TSelectParam:
    """
    查询单条数据, 如果未查询到则抛出 <NotFound> 异常

    :param statement: 查询语句
    :param nullable: 是否可以为空, 默认不允许为空, 不允许为空后将抛出异常
    :return:
    """
    async with get_session() as session:
        results = await session.exec(statement)
        data = results.first()

        if not nullable and not data:
            raise DatabaseNotFound()

        return data  # type: ignore


async def pagination(
    statement: Select[_TSelectParam] | SelectOfScalar[_TSelectParam],
    *,
    page: int = 1,
    size: int = 20,
) -> list[_TSelectParam]:
    """
    查询多条数据并进行分页

    :param statement: 查询的 sql 语句
    :param page: 当前页
    :param size: 每页大小
    :return:
    """
    async with get_session() as session:
        results = await session.exec(statement.offset(0 if page <= 1 else page - 1).limit(size))
        return [result for result in results.all()]


async def select_all(
    sql: Select[_TSelectParam] | SelectOfScalar[_TSelectParam],
) -> list[_TSelectParam]:
    """
    根据 SQL 查询符合条件的全部数据

    :param sql: SQLAlchemy 语句
    :return: 返回数据库信息列表
    """
    async with get_session() as session:
        results = await session.exec(sql)
        return [result for result in results.all()]


async def insert(table: Type[_TSelectParam], model: _TSelectParam) -> _TSelectParam:
    """
    向表中添加一个数据

    :param table: 要添加的模型表, 需要继承与 SQLModel 且 table = True
    :param model: 要添加的数据
    :return:
    """
    async with get_session() as session:
        data = table.model_validate(model)
        session.add(data)
        await session.commit()
        return data


async def update(table: _TSelectParam) -> _TSelectParam:
    """
    向表中更新一条数据

    :param table: 要更新的数据模型
    :return: 返回更新后的数据模型
    """
    async with get_session() as session:
        if hasattr(table, "updateTime"):
            table.updateTime = datetime.now()

        session.add(table)
        await session.commit()
        await session.refresh(table)

        return table


async def delete(
    statement: Select[_TSelectParam] | SelectOfScalar[_TSelectParam],
) -> _TSelectParam:
    """
    从表中删除一条数据

    :param statement: 查询条件的 SQL 语句
    :return:
    """
    async with get_session() as session:
        results = await session.exec(statement)
        data = results.first()

        if not data:
            raise DatabaseNotFound()

        await session.delete(data)
        await session.commit()

        return data
