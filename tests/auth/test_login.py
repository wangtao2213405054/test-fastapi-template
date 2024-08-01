# _author: Coke
# _date: 2024/7/30 下午10:17

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from tests.types import AsyncInit


@pytest.mark.asyncio
async def test_public_key(client: AsyncClient) -> None:
    """测试 /public/key 获取公钥接口"""

    response = await client.get("/auth/public/key")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_login(
    monkeypatch: pytest.MonkeyPatch,
    session: AsyncSession,
    client: AsyncClient,
    init: AsyncInit
) -> None:
    """测试 /user/login 接口"""

    from src.api.auth import service

    # 内存函数修改
    monkeypatch.setattr(service, "decrypt_message", lambda *args, **kwargs: "Ws123456!")
    monkeypatch.setattr(service, "check_password", lambda *args: True)

    response = await client.post("/auth/user/login", json={"password": "123456", "username": init.user.email})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_menu_list(client: AsyncClient, session: AsyncSession, init: AsyncInit) -> None:
    """测试 /menu/list 接口"""

    from src.api.auth.models import MenuTable

    menu = MenuTable(name="测试菜单", identifier="test")
    db_menu = MenuTable.model_validate(menu)
    session.add(db_menu)
    await session.commit()

    db_menu_json = db_menu.model_dump()
    db_menu_json["children"] = []

    response = await client.post("/auth/menu/list", json={})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK
    assert response.json()["data"] == [db_menu_json]


@pytest.mark.asyncio
async def test_edit_menu_info(client: AsyncClient, session: AsyncSession):
    """测试 /menu/edit 接口"""

    from src.api.auth.models import MenuTable

    add_response = await client.put("/auth/menu/edit", json={"name": "test", "identifier": "test"})

    assert add_response.status_code == status.HTTP_200_OK
    assert add_response.json()["code"] == status.HTTP_200_OK

    _id = add_response.json()["data"]["id"]

    add_result = await session.execute(select(MenuTable).where(MenuTable.id == _id))
    add_db_menu: MenuTable = add_result.scalars().first()
    add_db_menu_json = add_db_menu.model_dump()
    assert add_response.json()["data"] == add_db_menu_json

    update_response = await client.put("/auth/menu/edit", json={
        "id": _id,
        "name": "test1",
        "identifier": "test1"
    })

    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.json()["code"] == status.HTTP_200_OK

    update_result = await session.execute(select(MenuTable).where(MenuTable.id == _id))
    update_db_menu: MenuTable = update_result.scalars().first()
    update_db_menu_json = update_db_menu.model_dump()
    assert update_response.json()["data"] == update_db_menu_json


@pytest.mark.asyncio
async def test_delete_menu_info(client: AsyncClient, session: AsyncSession):
    """测试 /menu/delete 接口"""

    from src.api.auth.models import MenuTable

    menu = MenuTable(name="测试菜单", identifier="test")
    db_menu = MenuTable.model_validate(menu)
    session.add(db_menu)
    await session.commit()

    response = await client.request("DELETE", "/auth/menu/delete", json={"id": db_menu.id})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK

    delete_result = await session.execute(select(MenuTable).where(MenuTable.id == db_menu.id))
    delete_db_menu = delete_result.scalars().first()

    assert not delete_db_menu
