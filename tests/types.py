# _author: Coke
# _date: 2024/8/1 下午5:18
# _description: 在 Pytest 初始化数据库时写入的数据库内容

from pydantic import BaseModel

from src.api.manage.models import AffiliationTable, UserTable, RoleTable


class AsyncInit(BaseModel):
    """初始化数据库的表数据"""

    affiliation: AffiliationTable
    user: UserTable
    role: RoleTable
