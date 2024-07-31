from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src.main import app


@pytest.fixture(autouse=True, scope="session")
def run_migrations() -> None:
    """
    在测试会话开始时自动运行数据库迁移，并在测试会话结束后回滚迁移。

    这个 fixture 会在整个测试会话中只运行一次。它会确保在测试开始之前应用所有的数据库迁移，
    使测试环境中的数据库结构与应用程序代码保持一致。在测试结束后，它会回滚数据库迁移，
    将数据库恢复到基础版本，确保测试环境的干净和一致性。

    作用:
        - 在测试会话开始时，运行数据库迁移，将数据库升级到最新版本。
        - 在测试会话结束时，回滚数据库迁移，将数据库恢复到基础版本。
    :return:
    """
    # import os

    print("正在运行数据库迁移...")
    # os.system("alembic upgrade head")
    yield
    # os.system("alembic downgrade base")


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture 用于创建一个 `AsyncClient` 实例，以便进行 HTTP 请求。

    这个 fixture 设置了一个 `AsyncClient` 实例，指定了基础 URL 和 应用，
    并将其提供给测试函数。它会确保在测试完成后客户端被正确关闭。

    :return: AsyncGenerator[AsyncClient, None]: 一个异步生成器，生成 `AsyncClient` 实例。
    """

    transport = ASGITransport(app=app)  # type: ignore
    async with AsyncClient(transport=transport, base_url="http://localhost:8006/api/v1/client") as client:
        yield client
