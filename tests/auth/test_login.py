# _author: Coke
# _date: 2024/7/30 下午10:17
# _description: 测试登录相关接口

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from tests.types import AsyncInit


@pytest.mark.asyncio
async def test_public_key(client: AsyncClient) -> None:
    """测试 /public/key 获取公钥接口"""

    response = await client.get("/auth/public/key")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_login(
    monkeypatch: pytest.MonkeyPatch, session: AsyncSession, client: AsyncClient, init: AsyncInit
) -> None:
    """测试 /user/login 接口"""

    from src.api.auth import service

    # 内存函数修改
    monkeypatch.setattr(service, "decrypt_message", lambda *args, **kwargs: "Ws123456!")
    monkeypatch.setattr(service, "check_password", lambda *args: True)

    response = await client.post("/auth/user/login", json={"password": "123456", "username": init.user.email})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK
