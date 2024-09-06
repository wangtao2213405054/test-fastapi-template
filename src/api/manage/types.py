# _author: Coke
# _date: 2024/8/22 下午5:00
# _description: 系统管理请求体

from fastapi import Body
from pydantic import HttpUrl, field_validator

from src.models.types import CustomModel, GeneralKeywordPageRequestModel

# 菜单类型
MENU_DIRECTORY = 1  # 目录
MENU_ROUTE = 2  # 路由

# Icon 类型
ICON_ICONIFY = 1  # iconify 图标
ICON_LOCAL = 2  # 本地icon


class Query(CustomModel):
    key: str
    value: str


class SubPermission(CustomModel):
    code: str
    description: str | None = None


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
