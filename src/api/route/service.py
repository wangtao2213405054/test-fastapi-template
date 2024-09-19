# _author: Coke
# _date: 2024/9/12 上午10:25
# _description:

from sqlalchemy import ColumnElement
from sqlmodel import or_, select

from src import database
from src.api.manage.models import MenuListResponse, MenuTable, UserTable
from src.api.manage.types import ICON_ICONIFY, ICON_LOCAL, MENU_DIRECTORY

from .models import RouteMenuTreeResponse, RouteMeta


def transform_routes(menu_list: list[MenuListResponse]) -> list[RouteMenuTreeResponse]:
    """
    将菜单列表转换为路由树结构

    :param menu_list: 菜单列表
    :return: 路由树列表
    """

    routes: list[RouteMenuTreeResponse] = []

    for menu in menu_list:
        meta = RouteMeta(
            title=menu.menuName,
            i18nKey=menu.i18nKey,
            keepAlive=menu.keepAlive,
            constant=menu.constant,
            icon=menu.icon if menu.iconType == ICON_ICONIFY else None,
            localIcon=menu.icon if menu.iconType == ICON_LOCAL else None,
            order=menu.order or None,
            href=menu.href,
            hideInMenu=menu.hideInMenu,
            multiTab=menu.multiTab,
            fixedIndexInTab=menu.fixedIndexInTab,
            query=menu.query,
            homepage=menu.homepage,
        )

        route = RouteMenuTreeResponse(
            id=menu.id,
            name=menu.routeName,
            path=menu.routePath,
            component=menu.component,
            meta=meta,
            props=":" in menu.routePath,
        )

        if menu.menuType == MENU_DIRECTORY and menu.children:
            route.children = transform_routes(menu.children)

        routes.append(route)

    return routes


async def get_constant_route_tree() -> list[RouteMenuTreeResponse]:
    """
    获取常量路由树

    :return:
    """

    routes = await database.select_tree(
        MenuTable,
        MenuListResponse,
        node_id=0,
        clause_list=[MenuTable.constant == 1, MenuTable.status == 1],
    )

    return transform_routes(routes)  # type: ignore


async def get_user_route_tree(*, user: UserTable) -> list[RouteMenuTreeResponse]:
    """
    获取路由树

    :param user: 用户信息
    :return:
    """

    clause: list[ColumnElement[bool] | bool] = [MenuTable.constant == 0, MenuTable.status == 1]

    # 如果非常量路由并且不是超管
    if not user.isAdmin:
        # 如果未绑定角色或者角色未绑定路由则返回空列表
        if not user.role or not user.role.menuIds:
            return []

        clause.append(or_(*[MenuTable.id == menu_id for menu_id in user.role.menuIds]))

    routes = await database.select_tree(MenuTable, MenuListResponse, node_id=0, clause_list=clause)

    return transform_routes(routes)  # type: ignore


async def is_route_exist(*, name: str) -> bool:
    """
    查询当前路由是否存在

    :param name: 路由名称
    :return:
    """

    route = await database.select(select(MenuTable.routeName).where(MenuTable.routeName == name), nullable=True)

    return bool(route)
