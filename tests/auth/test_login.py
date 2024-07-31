# _author: Coke
# _date: 2024/7/30 下午10:17

import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_public_key(client: AsyncClient) -> None:
    """
    测试 /public/key 获取公钥接口

    :param client: <AsyncClient> 对象
    :return:
    """
    response = await client.get("/auth/public/key")
    print(response.json())
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_login(client: AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    from src.api.auth import service

    def fake_decrypt_password(password: str) -> str:
        return password

    response = await client.post("/auth/swagger/login", data={"password": "123456", "username": "admin"})
    print(response.json())
    assert response.status_code == status.HTTP_200_OK
