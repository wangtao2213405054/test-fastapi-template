# _author: Coke
# _date: 2023/12/11 23:00

from sqlmodel import Field, Relationship, select
from pydantic import field_validator

from src.models import BaseModel
from src.database import fetch_one


class GeneralBase(BaseModel):
    """ 通用数据模型 """
    name: str = Field(index=True)  # 名称
    identifier: str = Field(index=True, unique=True, nullable=False)  # 标识符


class RoleBase(GeneralBase):
    """ 角色数据模型 """
    name: str = Field(index=True)  # 名称
    identifier: str = Field(index=True, unique=True)  # 标识符


class RoleTable(RoleBase, table=True):
    """ 角色数据库模型 """
    __tablename__ = "test_role"
    id: int | None = Field(None, primary_key=True)

    users: list["UserTable"] = Relationship(back_populates="role")


class RoleCreate(RoleBase):
    """ 用于创建新的角色实例 """


class RoleRead(RoleBase):
    """ 读取角色实例 """
    id: int


class MenuBase(GeneralBase):
    """ 权限菜单数据库模型 """
    nodeId: int = Field(0, nullable=False, index=True)  # 节点ID


class MenuTable(MenuBase, table=True):
    """ 菜单数据库模型表 """
    __tablename__ = "test_menu"
    id: int | None = Field(None, primary_key=True)


class MenuCreate(MenuBase):
    """ 用于创建新的菜单实例 """


class MenuInfoResponse(MenuBase):
    id: int


class MenuListResponse(MenuBase):
    id: int
    children: list[MenuTable]


class UserBase(BaseModel):
    """ 用户数据模型 """
    name: str = Field(index=True)  # 名称
    email: str = Field(index=True, nullable=False, unique=True)  # 邮箱 不可重复
    mobile: str = Field(index=True, nullable=False, unique=True)  # 手机号 不可重复
    avatarUrl: str | None = None  # 头像
    state: bool = Field(True)  # 用户在职状态
    nodeId: int  # 节点
    roleId: int = Field(foreign_key="test_role.id")  # 角色ID
    # departmentId: int = Field(default=None, foreign_key="test_department.id")  # 部门


class UserPassword(UserBase):
    password: bytes  # 密码


class UserTable(UserPassword, table=True):
    __tablename__ = "test_user"
    id: int | None = Field(None, primary_key=True)
    role: RoleTable = Relationship(back_populates="users")  # 角色信息


class UserCreate(UserPassword):
    """ 用于创建新的实例 """


class UserRead(UserBase):
    """ 读取 User 实例 """
    id: int
