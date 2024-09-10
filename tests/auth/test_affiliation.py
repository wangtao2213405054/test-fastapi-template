# _author: Coke
# _date: 2024/8/5 16:01
# _description: 测试所属关系相关接口

import pytest
import pytest_asyncio
from fastapi import status
from httpx import AsyncClient
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.api.manage.models import AffiliationTable


class AffiliationDatabase(BaseModel):
    affiliation: AffiliationTable
    childrenAffiliation: AffiliationTable


@pytest_asyncio.fixture
async def database_to_affiliation_scope(session: AsyncSession) -> AffiliationDatabase:
    """
    当前文件的 fixture 用于数据库初始化信息。

    只在当前文件中生效。

    :param session: 数据库的 Session 信息
    :return:
    """

    affiliation = AffiliationTable(name="字节跳动")
    db_affiliation = AffiliationTable.model_validate(affiliation)
    session.add(db_affiliation)
    await session.commit()

    children_affiliation = AffiliationTable(name="抖音", nodeId=db_affiliation.id)
    db_children_affiliation = AffiliationTable.model_validate(children_affiliation)
    session.add(db_children_affiliation)
    await session.commit()

    return AffiliationDatabase(affiliation=db_affiliation, childrenAffiliation=db_children_affiliation)


@pytest.mark.asyncio
async def test_get_affiliation_list(
    client: AsyncClient, session: AsyncSession, database_to_affiliation_scope: AffiliationDatabase
) -> None:
    """测试 /affiliation/list 接口"""

    db_affiliation_json = database_to_affiliation_scope.affiliation.model_dump()
    db_children_affiliation_json = database_to_affiliation_scope.childrenAffiliation.model_dump()
    db_children_affiliation_json["children"] = []
    db_affiliation_json["children"] = [db_children_affiliation_json]

    response = await client.post("/manage/affiliation/list", json={})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK
    assert response.json()["data"] == [db_affiliation_json]


@pytest.mark.asyncio
async def test_get_affiliation_list_keyword(
    client: AsyncClient, session: AsyncSession, database_to_affiliation_scope: AffiliationDatabase
) -> None:
    """测试 /affiliation/list 接口 identifier关键字查询"""

    db_affiliation = database_to_affiliation_scope.childrenAffiliation
    db_affiliation_json = db_affiliation.model_dump()
    db_affiliation_json["children"] = []

    response = await client.post("/manage/affiliation/list", json={"keyword": db_affiliation.name})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK
    assert response.json()["data"] == [db_affiliation_json]


@pytest.mark.asyncio
async def test_get_affiliation_list_node(
    client: AsyncClient, session: AsyncSession, database_to_affiliation_scope: AffiliationDatabase
) -> None:
    """测试 /affiliation/list 接口 nodeId 关键字查询"""

    db_affiliation = database_to_affiliation_scope.childrenAffiliation
    db_affiliation_json = db_affiliation.model_dump()
    db_affiliation_json["children"] = []

    response = await client.post("/manage/affiliation/list", json={"nodeId": db_affiliation.nodeId})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK
    assert response.json()["data"] == [db_affiliation_json]


@pytest.mark.asyncio
async def test_get_affiliation_list_node_keyword(
    client: AsyncClient, session: AsyncSession, database_to_affiliation_scope: AffiliationDatabase
) -> None:
    """测试 /affiliation/list 接口 nodeId and keyword 关键字查询"""

    db_affiliation = database_to_affiliation_scope.affiliation
    db_affiliation_json = db_affiliation.model_dump()
    db_affiliation_json["children"] = []

    response = await client.post(
        "/manage/affiliation/list", json={"nodeId": db_affiliation.nodeId, "keyword": db_affiliation.name}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK
    assert response.json()["data"] == [db_affiliation_json]


@pytest.mark.asyncio
async def test_add_affiliation_info(client: AsyncClient, session: AsyncSession):
    """测试 /affiliation/edit 接口新增数据"""

    response = await client.put("/manage/affiliation/edit", json={"name": "西瓜视频"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK

    _id = response.json()["data"]["id"]

    result = await session.exec(select(AffiliationTable).where(AffiliationTable.id == _id))
    db_affiliation_json = result.first().model_dump()
    assert response.json()["data"] == db_affiliation_json


@pytest.mark.asyncio
async def test_update_affiliation_info(
    client: AsyncClient, session: AsyncSession, database_to_affiliation_scope: AffiliationDatabase
) -> None:
    """测试 /affiliation/edit 接口修改数据"""

    update_id = database_to_affiliation_scope.affiliation.id
    response = await client.put("/manage/affiliation/edit", json={"id": update_id, "name": "桃子"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK

    result = await session.exec(select(AffiliationTable).where(AffiliationTable.id == update_id))
    db_affiliation: AffiliationTable = result.first()
    db_affiliation_json = db_affiliation.model_dump()
    assert response.json()["data"] == db_affiliation_json


@pytest.mark.asyncio
async def test_delete_affiliation_info(
    client: AsyncClient, session: AsyncSession, database_to_affiliation_scope: AffiliationDatabase
) -> None:
    """测试 /affiliation/delete 接口"""

    affiliation = database_to_affiliation_scope.affiliation
    response = await client.request("DELETE", "/manage/affiliation/delete", json={"id": affiliation.id})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK

    delete_result = await session.exec(select(AffiliationTable).where(AffiliationTable.id == affiliation.id))
    delete_db_affiliation = delete_result.first()

    assert not delete_db_affiliation
