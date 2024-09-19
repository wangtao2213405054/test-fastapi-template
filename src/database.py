# _author: Coke
# _date: 2024/7/26 17:25
# _description: 数据库操作相关函数

import asyncio
from datetime import datetime
from functools import wraps
from typing import Any, Awaitable, Callable, Sequence, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import BinaryExpression, MetaData
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql.elements import ColumnElement
from sqlmodel import col, desc
from sqlmodel import select as _select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import Select, SelectOfScalar

from src.config import settings
from src.constants import DB_NAMING_CONVENTION
from src.exceptions import DatabaseNotFound, DatabaseUniqueError
from src.models.types import Pagination

_TSelectParam = TypeVar("_TSelectParam", bound=Any)
_TSelectResponse = TypeVar("_TSelectResponse", bound=Any)

# Mysql 数据库地址
DATABASE_URL = str(settings.DATABASE_URL)

engine = create_async_engine(DATABASE_URL, echo=settings.ENVIRONMENT.is_debug, pool_recycle=60)
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
                if func_key and kwargs.get(func_key):
                    clause.append(getattr(table, model_key) != kwargs.get(func_key))  # type: ignore

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
) -> Pagination[list[_TSelectParam]]:
    """
    查询多条数据并进行分页

    :param statement: 查询的 sql 语句
    :param page: 当前页
    :param size: 每页大小
    :return:
    """
    async with get_session() as session:
        results = await session.exec(statement.offset(0 if page <= 1 else page - 1).limit(size))
        total_count = await session.exec(statement)
        return Pagination(
            page=page, pageSize=size, total=len(total_count.all()), records=[result for result in results.all()]
        )


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


async def select_tree(
    table: Any,
    response_model: Type[_TSelectResponse],
    *,
    node_id: int,
    keyword: str = "",
    keyword_map_list: list[str] | None = None,
    recursion_id: str = "nodeId",
    clause_list: list[ColumnElement[bool] | bool] | None = None,
    page: int | None = None,
    size: int | None = None,
) -> list[_TSelectResponse] | Pagination[list[_TSelectResponse]]:
    """
    根据给定的 recursion_id 查询符合条件的树形结构数据。

    该函数会根据 recursion_id 和可选的关键字，递归地查询符合条件的树形结构数据。
    可以通过提供关键字和字段列表来进行搜索，也可以选择分页查询。

    :param table: 需要查询的数据库表类型。
    :param response_model: 用于构建响应的模型类型。
    :param node_id: 查询的节点 ID。
    :param keyword: 搜索关键字，用于在字段中匹配数据。
    :param keyword_map_list: 用于匹配的字段名称列表。如果提供了关键字，则会在这些字段中进行搜索。
    :param recursion_id: 递归关系中的字段名，默认值为 "nodeId"。
    :param clause_list: sql条件的列表
    :param page: 分页的页码，默认为 None 表示不分页。
    :param size: 分页的每页大小，默认为 None 表示不分页。

    :return: 符合条件的树形结构数据列表，每个元素都是 `response_model` 的实例。
    """

    clause: list[ColumnElement[bool] | bool] = clause_list or []

    if keyword_map_list and keyword:
        for keyword_map in keyword_map_list:
            clause.append(like(field=getattr(table, keyword_map), keyword=keyword))

    if node_id or not keyword:
        clause.append(getattr(table, recursion_id) == node_id)

    query = _select(table).where(*clause).order_by(desc(table.id))

    # 获取数据
    if isinstance(page, int) and isinstance(size, int):
        page_data: Pagination[list[_TSelectResponse]] | None = await pagination(query, page=page, size=size)
        tree_list = page_data.records if page_data is not None else []
    else:
        tree_list = await select_all(query)
        page_data = None

    # 获取子树
    tasks = [
        select_tree(
            table,
            response_model,
            node_id=item.id,
            keyword=keyword,
            keyword_map_list=keyword_map_list,
            recursion_id=recursion_id,
        )
        for item in tree_list
    ]
    children_list = await asyncio.gather(*tasks)

    # 构建树形结构
    tree_dict_list = [
        response_model(children=children, **item.model_dump()) for item, children in zip(tree_list, children_list)
    ]

    # 如果分页，将数据设置到分页对象中
    if page_data:
        page_data.records = tree_dict_list
        return page_data

    return tree_dict_list


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


async def batch_delete(statement: Select[_TSelectParam] | SelectOfScalar[_TSelectParam]) -> Sequence[_TSelectParam]:
    """
    从表中批量删除一组数据

    :param statement: 查询条件的 SQL 语句
    :return:
    """
    async with get_session() as session:
        results = await session.exec(statement)
        data = results.all()

        if not data:
            raise DatabaseNotFound()

        tasks = [session.delete(item) for item in data]
        await asyncio.gather(*tasks)
        await session.commit()

        return data
