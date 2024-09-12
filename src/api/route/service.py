# _author: Coke
# _date: 2024/9/12 上午10:25
# _description:

from sqlalchemy import ColumnElement
from sqlmodel import or_, select

from src import database
from src.api.manage.models import MenuTable, UserTable

from .models import RouteListResponse


async def get_constant_route_tree() -> list[RouteListResponse]:
    """
    获取常量路由树

    :return:
    """

    route = await database.select_tree(
        MenuTable, RouteListResponse, node_id=0, clause_list=[MenuTable.constant == True]
    )

    return route  # type: ignore


async def get_user_route_tree(*, user: UserTable) -> list[RouteListResponse]:
    """
    获取路由树

    :param user: 用户信息
    :return:
    """

    clause: list[ColumnElement[bool] | bool] = [MenuTable.constant == False]

    # 如果非常量路由并且不是超管
    if not user.isAdmin:
        # 如果未绑定角色或者角色未绑定路由则返回空列表
        if not user.role or not user.role.menuIds:
            return []

        clause.append(or_(*[MenuTable.id == menu_id for menu_id in user.role.menuIds]))

    route = await database.select_tree(MenuTable, RouteListResponse, node_id=0, clause_list=clause)

    return route  # type: ignore


async def is_route_exist(*, name: str) -> bool:
    """
    查询当前路由是否存在

    :param name: 路由名称
    :return:
    """

    route = await database.select(select(MenuTable.routeName).where(MenuTable.routeName == name), nullable=True)

    return bool(route)
