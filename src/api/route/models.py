# _author: Coke
# _date: 2024/9/12 上午10:25
# _description:

from src.api.manage.types import Query
from src.models.models import BaseNoCommonModel


class RouteMeta(BaseNoCommonModel):
    """路由Meta实例"""

    title: str
    i18nKey: str | None = None
    roles: list[str] = []
    keepAlive: bool = False
    constant: bool = False
    icon: str | None = None
    localIcon: str | None = None
    iconFontSize: int | None = None
    order: int | None = None
    href: str | None = None
    hideInMenu: bool = False
    activeMenu: str | None = None
    multiTab: bool = False
    fixedIndexInTab: int | None = None
    query: list[Query] | None = None
    homepage: bool = False


class RouteMenuTreeResponse(BaseNoCommonModel):
    """路由菜单结构树响应实例"""

    id: int
    name: str
    path: str
    component: str
    props: bool = False
    meta: RouteMeta
    children: list["RouteMenuTreeResponse"] = []
