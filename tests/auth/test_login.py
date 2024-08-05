# _author: Coke
# _date: 2024/7/30 下午10:17
# _description: 测试登录相关接口

import uuid
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
    from src import cache

    async def fake_set_redis_key(*args, **kwargs) -> None:  # type: ignore
        ...

    # 内存函数修改
    monkeypatch.setattr(service, "decrypt_message", lambda *args, **kwargs: "Ws123456!")
    monkeypatch.setattr(service, "check_password", lambda *args, **kwargs: True)
    monkeypatch.setattr(cache, "set_redis_key", fake_set_redis_key)

    response = await client.post("/auth/user/login", json={"password": "123456", "username": init.user.email})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_refresh_token(init: AsyncInit, client: AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """测试 /refresh/token 接口"""

    from src.api.auth.jwt import create_refresh_token
    from src.api.auth.models.types import JWTRefreshTokenData
    from src import cache

    _uuid = str(uuid.uuid4())

    async def fake_get_by_key(*args, **kwargs) -> str:  # type: ignore
        return _uuid

    async def fake_set_redis_key(*args, **kwargs) -> None:  # type: ignore
        ...

    monkeypatch.setattr(cache, "get_by_key", fake_get_by_key)
    monkeypatch.setattr(cache, "set_redis_key", fake_set_redis_key)

    _refresh_token = create_refresh_token(user=JWTRefreshTokenData(userId=init.user.id, uuid=_uuid))

    response = await client.post("/auth/refresh/token", json={"refreshToken": _refresh_token})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK
