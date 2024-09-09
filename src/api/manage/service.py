# _author: Coke
# _date: 2024/8/26 下午3:51
# _description:

from sqlmodel import select, or_

from src import database
from src.models.types import Pagination

from .models import MenuCreate, MenuInfoResponse, MenuListResponse, MenuTable
from .types import MENU_ROUTE, Query, SubPermission


async def get_menu_tree(
    *, node_id: int, keyword: str = "", page: int = 1, size: int = 20
) -> Pagination[list[MenuListResponse]]:
    """
    获取菜单树列表

    :param node_id: 节点ID
    :param keyword: 关键字
    :param page: 当前分页
    :param size: 当前分页数量
    :return: 菜单树列表
    """
    menu = await database.select_tree(
        MenuTable,
        MenuListResponse,
        node_id=node_id,
        keyword_map_list=["menuName", "routeName", "routePath"],
        keyword=keyword,
        page=page,
        size=size,
    )

    return menu  # type: ignore


@database.unique_check(
    MenuTable,
    func_key="menu_id",
    model_key="id",
    routePath=database.UniqueDetails(message="路由路径", kwargsKey="route_path"),
)
async def edit_menu(
    *,
    menu_id: int,
    component: str,
    node_id: int,
    menu_name: str,
    menu_type: int,
    route_name: str,
    route_path: str,
    i18n_key: str | None = None,
    order: int,
    icon_type: int,
    icon: str,
    status: bool,
    hide_in_menu: bool,
    multi_tab: bool,
    keep_alive: bool,
    href: str | None = None,
    constant: bool,
    fixed_index_in_tab: int | None = None,
    homepage: bool,
    query: list[Query],
    buttons: list[SubPermission],
    interfaces: list[SubPermission],
) -> MenuInfoResponse:
    """
    新增/修改一个路由菜单

    :param menu_id: 菜单ID，为真则代表修改
    :param component: 路由映射
    :param node_id: 节点ID
    :param menu_name: 菜单名称
    :param menu_type: 菜单类型
    :param route_name: 路由名称
    :param route_path: 路由路径
    :param i18n_key: 国际化Key
    :param order: 排序
    :param icon_type: icon 类型
    :param icon: icon
    :param status: 状态
    :param hide_in_menu: 是否隐藏此菜单
    :param multi_tab: 是否可以多选
    :param keep_alive: 缓存路由
    :param href: 是否为外链
    :param constant: 是否为常量路由
    :param fixed_index_in_tab: 如果设置了值，路由将在标签页中固定，并且值为固定标签的顺序
    :param homepage: 是否为首页路由
    :param query: 进入路由时默认携带的参数
    :param buttons: 按钮权限列表
    :param interfaces: 接口权限列表
    :return: 当前创建or修改后的菜单
    """
    if menu_id:
        menu = await database.select(select(MenuTable).where(MenuTable.id == menu_id))

        update_data = {
            "component": component,
            "nodeId": node_id,
            "menuName": menu_name,
            "menuType": menu_type,
            "routeName": route_name,
            "routePath": route_path,
            "i18nKey": i18n_key,
            "order": order,
            "iconType": icon_type,
            "icon": icon,
            "status": status,
            "hideInMenu": hide_in_menu,
            "multiTab": multi_tab,
            "keepAlive": keep_alive,
            "href": href,
            "constant": constant,
            "fixedIndexInTab": fixed_index_in_tab,
            "homepage": homepage,
            "query": [item.model_dump() for item in query],
            "buttons": [item.model_dump() for item in buttons],
            "interfaces": [item.model_dump() for item in interfaces],
        }

        for key, value in update_data.items():
            setattr(menu, key, value)

        update_menu = await database.update(menu)
        return MenuInfoResponse(**update_menu.model_dump())

    add_menu = await database.insert(
        MenuTable,
        MenuCreate(
            component=component,
            nodeId=node_id,
            menuName=menu_name,
            menuType=menu_type,
            routeName=route_name,
            routePath=route_path,
            i18nKey=i18n_key,
            order=order,
            iconType=icon_type,
            icon=icon,
            status=status,
            hideInMenu=hide_in_menu,
            multiTab=multi_tab,
            keepAlive=keep_alive,
            href=href,
            constant=constant,
            fixedIndexInTab=fixed_index_in_tab,
            homepage=homepage,
            query=query,
            buttons=buttons,
            interfaces=interfaces,
        ),
    )
    return MenuInfoResponse(**add_menu.model_dump())


async def delete_menu(*, menu_id: int) -> list[MenuInfoResponse]:
    """
    删除一个菜单及其子菜单

    该函数根据 `menu_id` 删除指定的菜单。

    :param menu_id: 菜单 ID
    :return: 删除的菜单的响应对象
    """
    menu = await database.batch_delete(
        select(MenuTable).where(or_(MenuTable.id == menu_id, MenuTable.nodeId == menu_id))
    )

    return [MenuInfoResponse(**item.model_dump()) for item in menu]


async def batch_delete_menu(*, menu_ids: list[int]) -> list[MenuInfoResponse]:
    """
    删除多个菜单及其子菜单

    该函数根据 `menu_ids` 删除指定的菜单。

    :param menu_ids: 菜单 ID 列表
    :return: None
    """

    menu = await database.batch_delete(
        select(MenuTable).where(
            or_(*[MenuTable.id == _id for _id in menu_ids], *[MenuTable.nodeId == _id for _id in menu_ids])
        )
    )

    return [MenuInfoResponse(**item.model_dump()) for item in menu]


async def get_page_list() -> Pagination[list[str]]:
    """
    获取页面列表

    :return: 页面列表
    """
    menu = await database.select_all(select(MenuTable.routeName).where(MenuTable.menuType == MENU_ROUTE))

    return menu  # type: ignore
