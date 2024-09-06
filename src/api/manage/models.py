# _author: Coke
# _date: 2024/8/26 下午3:22
# _description: 系统管理相关数据库响应模型


from pydantic import field_validator
from sqlmodel import JSON, Column, Field

from src.models import BaseModel

from .types import ICON_ICONIFY, MENU_DIRECTORY, Query, SubPermission


class MenuBase(BaseModel):
    """路由菜单数据模型"""

    component: str = Field(..., description="路由组件")
    nodeId: int = Field(0, description="节点ID")
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
    query: list[Query] = Field([], sa_column=Column(JSON), description="进入路由时默认携带的参数")
    buttons: list[SubPermission] = Field([], sa_column=Column(JSON), description="按钮权限")
    interfaces: list[SubPermission] = Field([], sa_column=Column(JSON), description="接口权限")

    # noinspection PyNestedDecorators
    @field_validator("query", mode="after")
    @classmethod
    def convert_query_to_dict(cls, query: list[Query]) -> list[dict]:
        return [item.model_dump() for item in query]

    # noinspection PyNestedDecorators
    @field_validator("buttons", mode="after")
    @classmethod
    def convert_buttons_to_dict(cls, buttons: list[SubPermission]) -> list[dict]:
        return [item.model_dump() for item in buttons]

    # noinspection PyNestedDecorators
    @field_validator("interfaces", mode="after")
    @classmethod
    def convert_interfaces_to_dict(cls, interfaces: list[SubPermission]) -> list[dict]:
        return [item.model_dump() for item in interfaces]


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
