# _author: Coke
# _date: 2024/8/5 下午4:37
# _description: 测试角色相关接口

import pytest
import pytest_asyncio
from fastapi import status
from httpx import AsyncClient
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.api.manage.models import MenuTable, RoleTable


class RoleDatabase(BaseModel):
    role: RoleTable
    supperRole: RoleTable
    menu: MenuTable


@pytest_asyncio.fixture
async def database_to_role_scope(session: AsyncSession) -> RoleDatabase:
    """
    当前文件的 fixture 用于数据库初始化信息。

    只在当前文件中生效。

    :param session: 数据库的 Session 信息
    :return:
    """

    menu = MenuTable(name="登录接口", identifier="/user/login")
    db_menu = MenuTable.model_validate(menu)
    session.add(db_menu)
    await session.commit()

    supper_role = RoleTable(name="超级管理员", describe="这是一个超级管理员权限, 可访问所有信息")
    db_supper_role = RoleTable.model_validate(supper_role)
    session.add(db_supper_role)
    await session.commit()

    role = RoleTable(
        name="普通管理员", describe="这是一个普通管理员权限, 可访问部分信息", menuIds=[db_menu.id]
    )
    db_role = RoleTable.model_validate(role)
    session.add(db_role)
    await session.commit()

    return RoleDatabase(role=db_role, menu=menu, supperRole=db_supper_role)


@pytest.mark.asyncio
async def test_get_role_list(client: AsyncClient, session: AsyncSession, database_to_role_scope: RoleDatabase) -> None:
    """测试 /role/list 接口"""

    db_role_json = database_to_role_scope.role.model_dump()
    db_supper_role_json = database_to_role_scope.supperRole.model_dump()

    response = await client.post("/manage/role/list", json={})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK
    assert response.json()["data"] == [db_supper_role_json, db_role_json]


@pytest.mark.asyncio
async def test_get_role_list_page(
    client: AsyncClient, session: AsyncSession, database_to_role_scope: RoleDatabase
) -> None:
    """测试 /role/list 分页条件"""

    db_supper_role_json = database_to_role_scope.supperRole.model_dump()

    page_size_response = await client.post("/manage/role/list", json={"page": 1, "pageSize": 1})

    assert page_size_response.status_code == status.HTTP_200_OK
    assert page_size_response.json()["code"] == status.HTTP_200_OK
    assert page_size_response.json()["data"] == [db_supper_role_json]

    page_response = await client.post("/manage/role/list", json={"page": 10, "pageSize": 1})

    assert page_response.status_code == status.HTTP_200_OK
    assert page_response.json()["code"] == status.HTTP_200_OK
    assert page_response.json()["data"] == []


@pytest.mark.asyncio
async def test_get_role_list_keyword(
    client: AsyncClient, session: AsyncSession, database_to_role_scope: RoleDatabase
) -> None:
    """测试 /role/list keyword关键字查询"""

    db_role_json = database_to_role_scope.role.model_dump()

    page_size_response = await client.post("/manage/role/list", json={"keyword": "普通管理员"})

    assert page_size_response.status_code == status.HTTP_200_OK
    assert page_size_response.json()["code"] == status.HTTP_200_OK
    assert page_size_response.json()["data"] == [db_role_json]


@pytest.mark.asyncio
async def test_add_role_info(client: AsyncClient, session: AsyncSession) -> None:
    """测试 /role/edit 接口新增数据"""

    response = await client.put("/manage/role/edit", json={"name": "外部角色"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK

    _id = response.json()["data"]["id"]

    result = await session.exec(select(RoleTable).where(RoleTable.id == _id))
    db_role_json = result.first().model_dump()

    assert response.json()["data"] == db_role_json


@pytest.mark.asyncio
async def test_update_role_info(
    client: AsyncClient, session: AsyncSession, database_to_role_scope: RoleDatabase
) -> None:
    """测试 /role/edit 接口修改数据"""

    role = database_to_role_scope.role

    response = await client.put(
        "/manage/role/edit", json={"id": role.id, "name": "修改后的超级管理员", "describe": "修改后的描述"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK

    result = await session.exec(select(RoleTable).where(RoleTable.id == role.id))
    db_role_json = result.first().model_dump()
    assert response.json()["data"] == db_role_json


@pytest.mark.asyncio
async def test_delete_role_info(
    client: AsyncClient, session: AsyncSession, database_to_role_scope: RoleDatabase
) -> None:
    """测试 /role/delete 接口"""

    role = database_to_role_scope.supperRole
    response = await client.request("DELETE", "/manage/role/delete", json={"id": role.id})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK

    delete_result = await session.exec(select(RoleTable).where(RoleTable.id == role.id))
    delete_db_menu = delete_result.first()

    assert not delete_db_menu
