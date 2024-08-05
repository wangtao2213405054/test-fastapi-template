# _author: Coke
# _date: 2024/8/5 下午4:37
# _description: 测试角色相关接口

import pytest
import pytest_asyncio

from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.api.auth.models.models import RoleTable


class RoleDatabase(BaseModel):
    role: RoleTable


@pytest_asyncio.fixture
async def database_to_affiliation_scope(session: AsyncSession) -> RoleDatabase:
    """
    当前文件的 fixture 用于数据库初始化信息。

    只在当前文件中生效。

    :param session: 数据库的 Session 信息
    :return:
    """

    role = RoleTable(name="超级管理员", describe="这是一个超级管理员权限, 可访问所有信息")
    db_role = RoleTable.model_validate(role)
    session.add(db_role)
    await session.commit()

    return RoleDatabase(role=db_role)
