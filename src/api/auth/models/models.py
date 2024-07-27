# _author: Coke
# _date: 2023/12/11 23:00
# _description: 认证相关数据库响应模型

from sqlmodel import Field, Relationship, Column, JSON
from src.models import BaseModel


class GeneralBase(BaseModel):
    """ 通用数据模型 """

    name: str = Field(index=True, description="名称")  # 名称


class IdentifierBase(GeneralBase):
    """ 带有标识符的模型 """

    identifier: str = Field(index=True, unique=True, nullable=False, description="标识符")  # 标识符


class RoleBase(IdentifierBase):
    """ 角色数据模型 """

    identifierList: list[str] = Field([], sa_column=Column(JSON), description="权限菜单标识符列表")  # 标识符


class RoleTable(RoleBase, table=True):
    """ 角色数据库模型 """

    __tablename__ = "test_role"
    id: int | None = Field(None, primary_key=True, description="ID")

    users: list["UserTable"] = Relationship(back_populates="role")


class RoleCreate(RoleBase):

    """ 用于创建新的角色实例 """


class RoleInfoResponse(RoleBase):
    """ 读取角色实例 """

    id: int


class MenuBase(IdentifierBase):
    """ 权限菜单数据库模型 """

    nodeId: int = Field(0, nullable=False, index=True, description="节点ID")  # 节点ID


class MenuTable(MenuBase, table=True):
    """ 菜单数据库模型表 """

    __tablename__ = "test_menu"
    id: int | None = Field(None, primary_key=True)


class MenuCreate(MenuBase):
    """ 用于创建新的菜单实例 """


class MenuInfoResponse(MenuBase):
    """ 菜单响应体 """
    id: int


class MenuListResponse(MenuBase):
    """ 菜单列表响应体 """

    id: int
    children: list[MenuInfoResponse]


class AffiliationBase(GeneralBase):
    """ 归属数据库表 """

    nodeId: int = Field(0, nullable=False, index=True, description="节点ID")  # 节点ID


class AffiliationTable(AffiliationBase, table=True):
    """ 人员归属数据库模型 """

    __tablename__ = "test_affiliation"
    id: int | None = Field(None, primary_key=True)

    users: list["UserTable"] = Relationship(back_populates="affiliation")


class AffiliationCreate(AffiliationBase):
    """ 用于创建新的归属实例 """


class AffiliationInfoResponse(AffiliationBase):
    """ 归属信息响应 """

    id: int


class AffiliationListResponse(AffiliationBase):
    """ 归属信息列表响应 """

    id: int
    children: list[AffiliationInfoResponse]


class UserBase(BaseModel):
    """ 用户数据模型 """

    name: str = Field(index=True, description="用户名称")  # 名称
    username: str = Field(index=True, description="用户名称拼音")
    email: str = Field(index=True, nullable=False, unique=True, description="邮箱")  # 邮箱 不可重复
    mobile: str = Field(index=True, nullable=False, unique=True, description="手机号")  # 手机号 不可重复
    avatarUrl: str | None = Field(None, description="头像")  # 头像
    status: bool = Field(True, description="用户在职状态")  # 用户在职状态
    roleId: int | None = Field(None, foreign_key="test_role.id", description="角色ID")  # 角色ID
    affiliationId: int = Field(default=None, foreign_key="test_affiliation.id", description="所属关系ID")  # 部门


class UserPassword(UserBase):
    """ 包含密码的用户数据模型 """

    password: bytes  # 密码


class UserTable(UserPassword, table=True):
    """ 用户数据库模型 """

    __tablename__ = "test_user"
    id: int | None = Field(None, primary_key=True)
    role: RoleTable = Relationship(back_populates="users")  # 角色信息
    affiliation: AffiliationTable = Relationship(back_populates="users")


class UserCreate(UserPassword):
    """ 用于创建新的实例 """


class UserResponse(UserBase):
    """ 读取 User 实例 """

    id: int
    resource: dict | None = None  # 用户的缓存资源
