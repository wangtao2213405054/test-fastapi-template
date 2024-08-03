# _author: Coke
# _date: 2024/8/3 下午8:05
# _description: 测试角色相关接口

import pytest
import pytest_asyncio
from fastapi import status
from httpx import AsyncClient
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.api.auth.models.models import MenuTable
from src.exceptions import status as status_code


class MenuDatabase(BaseModel):
    menu: MenuTable
    childrenMenu: MenuTable


@pytest_asyncio.fixture
async def database_to_menu_scope(session: AsyncSession) -> MenuDatabase:
    """
    当前文件的 fixture 用于数据库初始化信息。

    只在当前文件中生效。

    :param session: 数据库的 Session 信息
    :return:
    """

    menu = MenuTable(name="测试菜单", identifier="test")
    db_menu = MenuTable.model_validate(menu)
    session.add(db_menu)
    await session.commit()

    children_menu = MenuTable(name="子菜单", identifier="children", nodeId=db_menu.id)
    db_children_menu = MenuTable.model_validate(children_menu)
    session.add(db_children_menu)
    await session.commit()

    return MenuDatabase(menu=db_menu, childrenMenu=db_children_menu)


@pytest.mark.asyncio
async def test_get_menu_list(client: AsyncClient, session: AsyncSession, database_to_menu_scope: MenuDatabase) -> None:
    """测试 /menu/list 接口"""

    db_menu_json = database_to_menu_scope.menu.model_dump()
    db_children_menu_json = database_to_menu_scope.childrenMenu.model_dump()
    db_children_menu_json["children"] = []
    db_menu_json["children"] = [db_children_menu_json]

    response = await client.post("/auth/menu/list", json={})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK
    assert response.json()["data"] == [db_menu_json]


@pytest.mark.asyncio
async def test_get_menu_list_identifier(
    client: AsyncClient, session: AsyncSession, database_to_menu_scope: MenuDatabase
) -> None:
    """测试 /menu/list 接口 identifier关键字查询"""

    db_menu = database_to_menu_scope.childrenMenu
    db_menu_json = db_menu.model_dump()
    db_menu_json["children"] = []

    response = await client.post("/auth/menu/list", json={"keyword": db_menu.identifier})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK
    assert response.json()["data"] == [db_menu_json]


@pytest.mark.asyncio
async def test_get_menu_list_name(
    client: AsyncClient, session: AsyncSession, database_to_menu_scope: MenuDatabase
) -> None:
    """测试 /menu/list 接口 name关键字查询"""

    db_menu = database_to_menu_scope.childrenMenu
    db_menu_json = db_menu.model_dump()
    db_menu_json["children"] = []

    response = await client.post("/auth/menu/list", json={"keyword": db_menu.name})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK
    assert response.json()["data"] == [db_menu_json]


@pytest.mark.asyncio
async def test_get_menu_list_node(
    client: AsyncClient, session: AsyncSession, database_to_menu_scope: MenuDatabase
) -> None:
    """测试 /menu/list 接口 nodeId 关键字查询"""

    db_menu = database_to_menu_scope.childrenMenu
    db_menu_json = db_menu.model_dump()
    db_menu_json["children"] = []

    response = await client.post("/auth/menu/list", json={"nodeId": db_menu.nodeId})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK
    assert response.json()["data"] == [db_menu_json]


@pytest.mark.asyncio
async def test_get_menu_list_node_keyword(
    client: AsyncClient, session: AsyncSession, database_to_menu_scope: MenuDatabase
) -> None:
    """测试 /menu/list 接口 nodeId and keyword 关键字查询"""

    db_menu = database_to_menu_scope.menu
    db_menu_json = db_menu.model_dump()
    db_menu_json["children"] = []

    response = await client.post("/auth/menu/list", json={"nodeId": db_menu.nodeId, "keyword": db_menu.name})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK
    assert response.json()["data"] == [db_menu_json]


@pytest.mark.asyncio
async def test_add_menu_info(client: AsyncClient, session: AsyncSession):
    """测试 /menu/edit 接口新增数据"""

    response = await client.put("/auth/menu/edit", json={"name": "test", "identifier": "test"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK

    _id = response.json()["data"]["id"]

    result = await session.exec(select(MenuTable).where(MenuTable.id == _id))
    db_menu: MenuTable = result.first()
    db_menu_json = db_menu.model_dump()
    assert response.json()["data"] == db_menu_json


@pytest.mark.asyncio
async def test_add_menu_info_unique(
    client: AsyncClient, session: AsyncSession, database_to_menu_scope: MenuDatabase
) -> None:
    """测试 /menu/edit 接口重复添加"""

    db_menu = database_to_menu_scope.menu
    response = await client.put("/auth/menu/edit", json={"name": "test", "identifier": db_menu.identifier})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status_code.DATABASE_611_UNIQUE


@pytest.mark.asyncio
async def test_update_menu_info(client: AsyncClient, session: AsyncSession, database_to_menu_scope: MenuDatabase):
    """测试 /menu/edit 接口修改数据"""

    response = await client.put(
        "/auth/menu/edit", json={"id": database_to_menu_scope.menu.id, "name": "test1", "identifier": "test1"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK

    result = await session.exec(select(MenuTable).where(MenuTable.id == database_to_menu_scope.menu.id))
    db_menu: MenuTable = result.first()
    db_menu_json = db_menu.model_dump()
    assert response.json()["data"] == db_menu_json


@pytest.mark.asyncio
async def test_delete_menu_info(
    client: AsyncClient, session: AsyncSession, database_to_menu_scope: MenuDatabase
) -> None:
    """测试 /menu/delete 接口"""

    menu = database_to_menu_scope.menu
    response = await client.request("DELETE", "/auth/menu/delete", json={"id": menu.id})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK

    delete_result = await session.exec(select(MenuTable).where(MenuTable.id == menu.id))
    delete_db_menu = delete_result.first()

    assert not delete_db_menu
