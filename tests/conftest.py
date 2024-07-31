from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel.pool import StaticPool
from dotenv import load_dotenv


@pytest_asyncio.fixture
async def session() -> AsyncSession:
    """
    Fixture 用于创建和管理异步数据库会话。

    该 fixture 设置了一个异步 SQLite 数据库连接，创建所需的表，
    并提供一个会话实例以供测试使用。
    :return: 异步数据库会话实例
    """
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=True,
    )
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)

    async with async_session() as session:
        yield session


@pytest.fixture(scope="session", autouse=True)
def load_env() -> None:
    """
    Fixture 用于在会话级别自动加载环境变量。

    该 fixture 确保在任何测试执行之前，.env 文件中的环境变量被加载。
    :return:
    """
    load_dotenv()


@pytest_asyncio.fixture
async def client(session: AsyncSession, monkeypatch: pytest.MonkeyPatch) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture 用于创建一个 `AsyncClient` 实例，以便进行 HTTP 请求。

    这个 fixture 设置了一个 `AsyncClient` 实例，指定了基础 URL 和 应用，
    并将其提供给测试函数。它会确保在测试完成后客户端被正确关闭。

    :return: AsyncGenerator[AsyncClient, None]: 一个异步生成器，生成 `AsyncClient` 实例。
    """
    from src import database
    from src.main import app

    def get_session_override():
        return session

    monkeypatch.setattr(database, "get_session", get_session_override)

    transport = ASGITransport(app=app)  # type: ignore
    async with AsyncClient(transport=transport, base_url="http://localhost:8006/api/v1/client") as client:
        yield client
