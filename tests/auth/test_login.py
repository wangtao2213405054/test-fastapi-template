# _author: Coke
# _date: 2024/7/30 下午10:17

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status


@pytest.mark.asyncio
async def test_public_key(client: AsyncClient) -> None:
    """测试 /public/key 获取公钥接口"""

    response = await client.get("/auth/public/key")
    print(response.json())
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_login(monkeypatch: pytest.MonkeyPatch, session: AsyncSession, client: AsyncClient) -> None:
    """测试 /user/login 接口"""

    from src.api.auth import service

    def fake_decrypt_message(*args, **kwargs) -> str:
        return "Ws123456!"

    def fake_check_password(*args, **kwargs) -> bool:
        return True

    # 内存函数修改
    monkeypatch.setattr(service, "decrypt_message", fake_decrypt_message)
    monkeypatch.setattr(service, "check_password", fake_check_password)

    from src.api.auth import security
    from src.api.auth.models.models import UserTable, UserCreate

    # 向内存数据库添加数据
    user = UserCreate(
        email="admin@qq.com",
        password=security.hash_password("123456"),
        name="test",
        username="test",
        mobile="18888888888",
        affiliationId=1
    )
    user_db = UserTable.model_validate(user)
    session.add(user_db)
    await session.commit()

    response = await client.post(
        "/auth/user/login",
        json={"password": "123456", "username": "admin@qq.com"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_menu_list(client: AsyncClient, session: AsyncSession, init) -> None:
    """测试 /menu/list 接口"""

    from src.api.auth.models import MenuTable

    menu = MenuTable(
        name="测试菜单",
        identifier="test"
    )
    db_menu = MenuTable.model_validate(menu)
    session.add(db_menu)
    await session.commit()

    db_menu_json = db_menu.model_dump()
    db_menu_json["children"] = []

    response = await client.post(
        "/auth/menu/list",
        json={}
    )

    print(init.affiliation, "11223344")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK
    assert response.json()["data"] == [db_menu_json]
