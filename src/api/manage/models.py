# _author: Coke
# _date: 2023/12/11 23:00
# _description: 系统管理相关数据库响应模型

from pydantic import Field as PydanticField
from sqlmodel import JSON, Column, Field, Relationship

from src.models import BaseModel

from .types import ICON_ICONIFY, MENU_DIRECTORY, Query, SubPermission


class GeneralBase(BaseModel):
    """通用数据模型"""

    name: str = Field(index=True, description="名称", schema_extra={"examples": ["name"]})  # 名称


class IdentifierBase(GeneralBase):
    """带有标识符的模型"""

    identifier: str = Field(
        index=True, unique=True, description="标识符", schema_extra={"examples": ["identifier"]}
    )  # 标识符


class RoleBase(GeneralBase):
    """角色数据模型"""

    describe: str | None = Field(None, description="角色描述信息")
    status: bool = Field(True, description="角色状态")
    menuIds: list[int] = Field([], sa_column=Column(JSON), description="权限菜单ID列表")
    buttonCodes: list[str] = Field([], sa_column=Column(JSON), description="按钮权限code列表")
    interfaceCodes: list[str] = Field([], sa_column=Column(JSON), description="接口权限code列表")


class RoleTable(RoleBase, table=True):
    """角色数据库模型"""

    __tablename__ = "test_role"
    id: int | None = Field(None, primary_key=True, description="ID")

    users: list["UserTable"] = Relationship(back_populates="role")


class RoleCreate(RoleBase):
    """用于创建新的角色实例"""


class RoleInfoResponse(RoleBase):
    """读取角色实例"""

    id: int


class AffiliationBase(GeneralBase):
    """归属数据库表"""

    nodeId: int = Field(0, index=True, description="节点ID")  # 节点ID


class AffiliationTable(AffiliationBase, table=True):
    """人员归属数据库模型"""

    __tablename__ = "test_affiliation"
    id: int | None = Field(None, primary_key=True)

    users: list["UserTable"] = Relationship(back_populates="affiliation")


class AffiliationCreate(AffiliationBase):
    """用于创建新的归属实例"""


class AffiliationInfoResponse(AffiliationBase):
    """归属信息响应"""

    id: int


class AffiliationListResponse(AffiliationBase):
    """归属信息列表响应"""

    id: int
    children: list["AffiliationListResponse"] = PydanticField(
        [],
        examples=[
            [
                {
                    "id": 2,
                    "name": "name",
                    "nodeId": 1,
                    "children": [],
                }
            ]
        ],
    )


class UserBase(BaseModel):
    """用户数据模型"""

    name: str = Field(index=True, description="用户名称")  # 名称
    username: str = Field(index=True, description="用户名称拼音")
    email: str = Field(index=True, unique=True, description="邮箱")  # 邮箱 不可重复
    mobile: str = Field(index=True, unique=True, description="手机号")  # 手机号 不可重复
    avatarUrl: str | None = Field(None, description="头像")  # 头像
    status: bool = Field(True, description="用户在职状态")  # 用户在职状态
    isAdmin: bool = Field(False, description="是否为超管")
    roleId: int | None = Field(None, foreign_key="test_role.id", description="角色ID")  # 角色ID
    affiliationId: int | None = Field(None, foreign_key="test_affiliation.id", description="所属关系ID")  # 部门


class UserPassword(UserBase):
    """包含密码的用户数据模型"""

    password: bytes  # 密码


class UserTable(UserPassword, table=True):
    """用户数据库模型"""

    __tablename__ = "test_user"
    id: int | None = Field(None, primary_key=True)
    role: RoleTable | None = Relationship(back_populates="users")  # 角色信息
    affiliation: AffiliationTable | None = Relationship(back_populates="users")


class UserCreate(UserPassword):
    """用于创建新的实例"""


class UserResponse(UserBase):
    """读取 User 实例"""

    id: int
    resource: dict | None = None  # 用户的缓存资源
    roles: list[str] = []


class RouteBase(BaseModel):
    """路由模型"""

    nodeId: int = Field(0, description="节点ID")
    component: str = Field(..., description="路由组件")
    menuName: str = Field(..., description="菜单名称")
    menuType: int = Field(MENU_DIRECTORY, description="菜单类型")
    routeName: str = Field(..., description="路由名称")
    routePath: str = Field(..., unique=True, description="路由路径")
    i18nKey: str | None = Field(None, description="国际化Key")
    order: int = Field(1, description="排序")
    iconType: int = Field(ICON_ICONIFY, description="icon类型")
    icon: str = Field(..., description="icon地址")
    status: bool = Field(True, description="菜单状态")
    hideInMenu: bool = Field(False, description="隐藏菜单")
    multiTab: bool = Field(False, description="是否支持多标签页")
    keepAlive: bool = Field(False, description="缓存路由")
    href: str | None = Field(None, description="外链地址")
    constant: bool = Field(False, description="是否为常量路由")
    fixedIndexInTab: int | None = Field(None, description="如果设置了值，路由将在标签页中固定，并且值为固定标签的顺序")
    homepage: bool = Field(True, description="如果为真则此路由将进入首页，否则详情页")


class MenuBase(RouteBase):
    """路由菜单数据模型"""

    query: list[Query] = Field([], sa_column=Column(JSON), description="进入路由时默认携带的参数")
    buttons: list[SubPermission] = Field([], sa_column=Column(JSON), description="按钮权限")
    interfaces: list[SubPermission] = Field([], sa_column=Column(JSON), description="接口权限")


class MenuTable(MenuBase, table=True):
    """菜单数据库模型"""

    __tablename__ = "test_menu"

    id: int | None = Field(None, primary_key=True, description="菜单ID")


class MenuCreate(MenuBase):
    """创建菜单实例"""


class MenuInfoResponse(MenuBase):
    """菜单信息响应实例"""

    id: int


class MenuListResponse(MenuInfoResponse):
    """菜单列表响应实例"""

    children: list["MenuListResponse"] = []


class MenuSimplifyListResponse(BaseModel):
    """简化后的菜单响应体"""

    id: int
    nodeId: int
    menuName: str
    children: list["MenuSimplifyListResponse"] = []


class MenuPermissionTreeResponse(BaseModel):
    """菜单权限树的响应体"""

    key: str
    label: str
    value: str
    disabled: bool
    children: list["MenuPermissionTreeResponse"] = []
