# _author: Coke
# _date: 2024/7/25 13:10
# _description: 系统管理相关请求模型

from fastapi import Body
from pydantic import EmailStr, HttpUrl, field_validator

from src.models.types import (
    CustomModel,
    GeneralKeywordPageRequestModel,
    GeneralKeywordRequestModel,
)
from src.utils import validate


class UserBaseRequest(CustomModel):
    """用户基础请求类"""

    name: str = Body(..., description="用户名称", min_length=2, max_length=128)
    email: EmailStr = Body(..., description="邮箱", min_length=6, max_length=128)
    mobile: str = Body(..., description="手机号", min_length=11, max_length=11, examples=["18888888888"])
    avatarUrl: HttpUrl | None = Body(None, description="用户头像地址")
    roleId: int | None = Body(None, description="所属的角色ID")
    affiliationId: int | None = Body(None, description="用户所属的关系")

    # noinspection PyNestedDecorators
    @field_validator("mobile", mode="after")
    @classmethod
    def valid_mobile(cls, mobile: str) -> str:
        if not validate.phone_number(mobile):
            raise ValueError("手机号错误")

        return mobile


class CreateUserRequest(UserBaseRequest):
    """创建用户请求模型"""

    password: str = Body(..., description="密码")  # RSA 加密后的密码


class UpdateUserInfoRequest(UserBaseRequest):
    """更改用户信息请求模型"""

    id: int = Body(..., description="用户ID")
    status: bool = Body(True, description="在职状态")


class UpdatePasswordRequest(CustomModel):
    """修改密码的请求模型"""

    id: int = Body(..., description="用户ID")
    oldPassword: str = Body(..., description="旧的密码")
    newPassword: str = Body(..., description="新的密码")


class AuthEditRoleRequest(CustomModel):
    """修改角色信息请求体"""

    id: int = Body(0, description="角色ID")
    name: str = Body(..., description="角色名称")
    describe: str | None = Body(None, description="角色描述")
    status: bool = Body(True, description="角色状态")


class ManageEditRolePermissionRequest(CustomModel):
    id: int = Body(..., description="角色ID")
    menuIds: list[int] | None = Body(None, description="菜单权限ID列表")
    buttonCodes: list[str] | None = Body(None, description="按钮权限code列表")
    interfaceCodes: list[str] | None = Body(None, description="接口权限code列表")


class AuthGetRoleListRequest(GeneralKeywordPageRequestModel):
    """获取角色列表的请求体"""

    status: bool | None = Body(None, description="角色状态查询")


class AuthEditAffiliationRequest(CustomModel):
    """修改/新增 所属关系的请求体"""

    id: int = Body(0, description="所属关系ID")
    name: str = Body(..., description="所属关系名称")
    nodeId: int = Body(0, description="所属节点ID")


class AuthGetAffiliationListRequest(GeneralKeywordRequestModel):
    """获取所属关系列表的请求体"""

    nodeId: int = Body(0, description="节点ID")


# 菜单类型
MENU_DIRECTORY = 1  # 目录
MENU_ROUTE = 2  # 路由

# Icon 类型
ICON_ICONIFY = 1  # iconify 图标
ICON_LOCAL = 2  # 本地icon

# 权限类型
PERMISSION_BUTTONS = "buttons"  # button 权限
PERMISSION_INTERFACE = "interfaces"  # interface 权限


class Query(CustomModel):
    key: str
    value: str

    # noinspection PyNestedDecorators
    @field_validator("key", mode="after")
    @classmethod
    def valid_key(cls, key: str) -> str:
        if not key:
            raise ValueError("参数Key不可为空")

        return key

    # noinspection PyNestedDecorators
    @field_validator("value", mode="after")
    @classmethod
    def valid_value(cls, value: str) -> str:
        if not value:
            raise ValueError("参数值不可为空")

        return value


class SubPermission(CustomModel):
    code: str
    description: str

    # noinspection PyNestedDecorators
    @field_validator("code", mode="after")
    @classmethod
    def valid_code(cls, code: str) -> str:
        if not code:
            raise ValueError("标识不可为空")

        return code

    # noinspection PyNestedDecorators
    @field_validator("description", mode="after")
    @classmethod
    def valid_description(cls, description: str) -> str:
        if not description:
            raise ValueError("描述不可为空")

        return description


class ManageGetMenuListRequest(GeneralKeywordPageRequestModel):
    """获取菜单列表的请求体"""

    nodeId: int = Body(0, description="节点ID")


class ManageEditMenuRequest(CustomModel):
    """修改权限菜单请求"""

    id: int = Body(0, description="菜单ID")
    component: str = Body(..., description="路由组件")
    nodeId: int = Body(0, description="节点ID")
    menuName: str = Body(..., description="菜单名称")
    menuType: int = Body(MENU_DIRECTORY, description="菜单类型")
    routeName: str = Body(..., description="路由名称")
    routePath: str = Body(..., description="路由路径")
    i18nKey: str | None = Body(None, description="国际化Key")
    order: int = Body(1, description="排序")
    iconType: int = Body(ICON_ICONIFY, description="icon类型")
    icon: str = Body(..., description="icon地址")
    status: bool = Body(True, description="菜单状态")
    hideInMenu: bool = Body(False, description="隐藏菜单")
    multiTab: bool = Body(False, description="是否支持多标签页")
    keepAlive: bool = Body(False, description="缓存路由")
    href: HttpUrl | None = Body(None, description="外链地址")
    constant: bool = Body(False, description="是否为常量路由")
    fixedIndexInTab: int | None = Body(None, description="如果设置了值，路由将在标签页中固定，并且值为固定标签的顺序")
    homepage: bool = Body(True, description="如果为真则此路由将进入首页，否则详情页")
    query: list[Query] = Body([], description="进入路由时默认携带的参数")
    buttons: list[SubPermission] = Body([], description="按钮权限")
    interfaces: list[SubPermission] = Body([], description="接口权限")

    # noinspection PyNestedDecorators
    @field_validator("menuType", mode="after")
    @classmethod
    def valid_menu_type(cls, menu_type: str) -> str:
        if menu_type not in (MENU_DIRECTORY, MENU_ROUTE):
            raise ValueError("菜单类型错误")

        return menu_type

    # noinspection PyNestedDecorators
    @field_validator("iconType", mode="after")
    @classmethod
    def valid_icon_type(cls, icon_type: str) -> str:
        if icon_type not in (ICON_ICONIFY, ICON_LOCAL):
            raise ValueError("icon类型错误")

        return icon_type

    # noinspection PyNestedDecorators
    @field_validator("routePath", mode="after")
    @classmethod
    def valid_route_path(cls, route_path: str) -> str:
        if not route_path.startswith("/"):
            raise ValueError('路由路径必须以"/"开头')

        return route_path


class ManageGetDetailPermissionRequest(CustomModel):
    """获取详细权限菜单请求"""

    menuType: str = Body(PERMISSION_BUTTONS, description="菜单类型")

    # noinspection PyNestedDecorators
    @field_validator("menuType", mode="after")
    @classmethod
    def valid_menu_type(cls, menu_type: str) -> str:
        if menu_type not in (PERMISSION_BUTTONS, PERMISSION_INTERFACE):
            raise ValueError("菜单类型错误")

        return menu_type
