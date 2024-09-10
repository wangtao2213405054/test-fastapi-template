# _author: Coke
# _date: 2024/7/30 下午10:17
# _description: 测试登录相关接口

import uuid
import pytest
import pytest_asyncio
from fastapi import status
from httpx import AsyncClient, ASGITransport
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from tests.types import AsyncInit
from typing import AsyncGenerator


@pytest_asyncio.fixture
async def client(
    request: pytest.FixtureRequest, session: AsyncSession, monkeypatch: pytest.MonkeyPatch, init: AsyncInit
) -> AsyncGenerator[AsyncClient, None]:
    """重写了 conf test 文件中的 client fixture 使其支持Token校验"""

    from src import database
    from src.config import settings
    from src.main import app
    from src.api.manage.jwt import create_access_token
    from src.api.manage.jwt import validate_permission
    from src.api.manage.types import JWTData

    # 使用内存修改工具修改 get_session 类
    monkeypatch.setattr(database, "get_session", lambda: session)

    app.dependency_overrides[validate_permission] = validate_permission  # type: ignore

    transport = ASGITransport(app=app)  # type: ignore
    token = create_access_token(user=JWTData(userId=init.user.id))

    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=transport, headers=headers, base_url=f"https://{settings.PREFIX}") as client:
        yield client


@pytest.mark.asyncio
async def test_public_key(client: AsyncClient) -> None:
    """测试 /public/key 获取公钥接口"""

    response = await client.get("/manage/public/key")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_login(
    monkeypatch: pytest.MonkeyPatch, session: AsyncSession, client: AsyncClient, init: AsyncInit
) -> None:
    """测试 /user/login 接口"""

    from src import cache
    from src.api.manage import service

    async def fake_set_redis_key(*args, **kwargs) -> None:  # type: ignore
        ...

    # 内存函数修改
    monkeypatch.setattr(service, "decrypt_message", lambda *args, **kwargs: "Ws123456!")
    monkeypatch.setattr(service, "check_password", lambda *args, **kwargs: True)
    monkeypatch.setattr(cache, "set_redis_key", fake_set_redis_key)

    response = await client.post("/manage/user/login", json={"password": "123456", "username": init.user.email})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_refresh_token(init: AsyncInit, client: AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """测试 /refresh/token 接口"""

    from src import cache
    from src.api.manage.jwt import create_refresh_token
    from src.api.manage.types import JWTRefreshTokenData

    _uuid = str(uuid.uuid4())

    async def fake_get_by_key(*args, **kwargs) -> str:  # type: ignore
        return _uuid

    async def fake_set_redis_key(*args, **kwargs) -> None:  # type: ignore
        ...

    monkeypatch.setattr(cache, "get_by_key", fake_get_by_key)
    monkeypatch.setattr(cache, "set_redis_key", fake_set_redis_key)

    _refresh_token = create_refresh_token(user=JWTRefreshTokenData(userId=init.user.id, uuid=_uuid))

    response = await client.post("/manage/refresh/token", json={"refreshToken": _refresh_token})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_user_info(client: AsyncClient, init: AsyncInit) -> None:
    """测试 /user/info 接口"""

    from src.api.manage.models import UserResponse
    from src.api.manage.jwt import create_access_token
    from src.api.manage.types import JWTData

    token = create_access_token(user=JWTData(userId=init.user.id))
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = await client.get("/manage/user/info")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK
    assert response.json()["data"] == UserResponse(**init.user.model_dump()).model_dump()


@pytest.mark.asyncio
async def test_user_info_not_token(client: AsyncClient, init: AsyncInit) -> None:
    """测试 /user/info 接口 验证Token"""

    client.headers.update({"Authorization": ""})
    response = await client.get("/manage/user/info")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_user_info_not_permission(client: AsyncClient, session: AsyncSession) -> None:
    """测试 /user/info 接口 验证Token"""

    from src.api.manage import security
    from src.api.manage.models import UserCreate, UserTable
    from src.api.manage.jwt import create_access_token
    from src.api.manage.types import JWTData

    user = UserCreate(
        email="permission@qq.com",
        password=security.hash_password("123456"),
        name="permission",
        username="permission",
        mobile="17777777777",
        isAdmin=False,
    )
    db_user = UserTable.model_validate(user)
    session.add(db_user)
    await session.commit()

    token = create_access_token(user=JWTData(userId=db_user.id))
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = await client.get("/manage/user/info")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_user_create(
    client: AsyncClient, session: AsyncSession, monkeypatch: pytest.MonkeyPatch, init: AsyncInit
) -> None:
    """测试 /user/create 接口"""

    from src.api.manage import service
    from src.api.manage.models import UserTable, UserResponse

    monkeypatch.setattr(service, "decrypt_password", lambda password: password)

    response = await client.post("/manage/user/create", json={
        "name": "测试账号",
        "email": "coke@test.cn",
        "mobile": "11012011991",
        "password": "Ck123456!",
        "affiliationId": init.affiliation.id,
        "roleId": init.role.id,
    })

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK

    _id = response.json()["data"]["id"]

    user = await session.exec(select(UserTable).where(UserTable.id == _id))
    db_user: UserTable = user.first()

    assert response.json()["data"] == UserResponse(**db_user.model_dump()).model_dump()


@pytest.mark.asyncio
async def test_user_update(client: AsyncClient, session: AsyncSession, init: AsyncInit) -> None:
    """测试 /user/update 接口"""

    from src.api.manage.models import UserTable, UserResponse

    response = await client.post("/manage/user/update", json={
        "name": "测试账号",
        "email": "coke@test.cn",
        "mobile": "11012011991",
        "affiliationId": init.affiliation.id,
        "roleId": init.role.id,
        "id": init.user.id,
    })

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK

    user = await session.exec(select(UserTable).where(UserTable.id == init.user.id))
    db_user = user.first()

    assert response.json()["data"] == UserResponse(**db_user.model_dump()).model_dump()


@pytest.mark.asyncio
async def test_update_password(
        client: AsyncClient, session: AsyncSession, init: AsyncInit, monkeypatch: pytest.MonkeyPatch
) -> None:
    """测试 /update/password 接口"""

    from src.api.manage.models import UserTable
    from src.api.manage import service
    from src.api.manage.security import check_password

    monkeypatch.setattr(service, "decrypt_password", lambda password: password)
    monkeypatch.setattr(service, "check_password", lambda *args, **kwargs: True)

    new_password = "<PASSWORD>"
    body = {
        "id": init.user.id,
        "oldPassword": "123444",
        "newPassword": new_password,
    }

    response = await client.post("/manage/update/password", json=body)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK

    user = await session.exec(select(UserTable).where(UserTable.id == init.user.id))
    db_user: UserTable = user.first()

    assert check_password(new_password, db_user.password)
