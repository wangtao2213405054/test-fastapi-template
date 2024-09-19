# _author: Coke
# _date: 2024/9/14 上午10:16
# _description:

from sqlmodel import Session

from src.api.auth.security import hash_password
from src.api.manage.models import MenuTable, UserTable
from src.api.manage.types import ICON_ICONIFY, MENU_DIRECTORY, MENU_ROUTE


def menu(session: Session) -> None:
    """
    默认菜单
    :param session:
    :return:
    """

    constant_menus: list[MenuTable] = [
        MenuTable(
            component="layout.blank$view.403",
            menuName="403",
            menuType=MENU_ROUTE,
            routeName="403",
            routePath="/403",
            iconType=ICON_ICONIFY,
            icon="ic:baseline-block",
            status=True,
            hideInMenu=True,
            constant=True,
            homepage=False,
        ),
        MenuTable(
            component="layout.blank$view.404",
            menuName="404",
            menuType=MENU_ROUTE,
            routeName="404",
            routePath="/404",
            iconType=ICON_ICONIFY,
            icon="ic:baseline-web-asset-off",
            status=True,
            hideInMenu=True,
            constant=True,
            homepage=False,
        ),
        MenuTable(
            component="layout.blank$view.500",
            menuName="500",
            menuType=MENU_ROUTE,
            routeName="500",
            routePath="/500",
            iconType=ICON_ICONIFY,
            icon="ic:baseline-wifi-off",
            status=True,
            hideInMenu=True,
            constant=True,
            homepage=False,
        ),
        MenuTable(
            component="layout.base$view.iframe-page",
            menuName="框架页面",
            menuType=MENU_ROUTE,
            routeName="iframe-page",
            routePath="/iframe-page/:url",
            iconType=ICON_ICONIFY,
            icon="material-symbols:iframe",
            status=True,
            hideInMenu=True,
            constant=True,
            homepage=False,
        ),
        MenuTable(
            component="layout.blank$view.login",
            menuName="登录",
            menuType=MENU_ROUTE,
            routeName="login",
            routePath="/login/:module(pwd-login|code-login|register|reset-pwd|bind-wechat)?",
            iconType=ICON_ICONIFY,
            icon="ant-design:login-outlined",
            status=True,
            hideInMenu=True,
            constant=True,
            homepage=False,
        ),
    ]

    _manage = MenuTable(
        component="layout.home",
        menuName="系统管理",
        menuType=MENU_DIRECTORY,
        routeName="manage",
        routePath="/manage",
        iconType=ICON_ICONIFY,
        icon="carbon:cloud-service-management",
    )

    parent_menu = [_manage]

    session.add_all(constant_menus + parent_menu)
    session.commit()
    user_menus: list[MenuTable] = [
        MenuTable(
            component="view.manage_menu",
            menuName="菜单管理",
            menuType=MENU_ROUTE,
            routeName="manage_menu",
            routePath="/manage/menu",
            iconType=ICON_ICONIFY,
            icon="material-symbols:route",
            nodeId=_manage.id,  # type: ignore
            interfaces=[
                dict(code="/manage/getMenuList", description="获取菜单列表接口"),  # type: ignore
                dict(code="/manage/editMenuInfo", description="新增/修改菜单接口"),  # type: ignore
                dict(code="/manage/deleteMenu", description="删除菜单接口"),  # type: ignore
                dict(code="/manage/batchDeleteMenu", description="批量删除菜单接口"),  # type: ignore
                dict(code="/manage/getPageAll", description="获取当前所有的页面"),  # type: ignore
                dict(code="/manage/getRouterMenuAll", description="获取简化后的路由菜单列表"),  # type: ignore
                dict(code="/manage/getPermissionMenuAll", description="通过菜单类型获取对应的列表"),  # type: ignore
            ],
            buttons=[
                dict(code="manage.menu.add", description="添加菜单"),  # type: ignore
                dict(code="manage.menu.edit", description="编辑菜单"),  # type: ignore
                dict(code="manage.menu.delete", description="删除菜单"),  # type: ignore
                dict(code="manage.menu.batchDelete", description="批量删除菜单"),  # type: ignore
            ],
        ),
        MenuTable(
            component="view.manage_role",
            menuName="角色管理",
            menuType=MENU_ROUTE,
            routeName="manage_role",
            routePath="/manage/role",
            iconType=ICON_ICONIFY,
            icon="carbon:user-role",
            nodeId=_manage.id,  # type: ignore
            interfaces=[
                dict(code="/manage/editRoleInfo", description="新增/修改角色信息"),  # type: ignore
                dict(code="/manage/updateRolePermission", description="更新当前角色的权限信息"),  # type: ignore
                dict(code="/manage/getRoleList", description="获取角色列表接口"),  # type: ignore
                dict(code="/manage/deleteRole", description="删除角色信息接口"),  # type: ignore
                dict(code="/manage/batchDeleteRole", description="批量删除角色信息接口"),  # type: ignore
            ],
            buttons=[
                dict(code="manage.role.add", description="添加角色"),  # type: ignore
                dict(code="manage.role.edit", description="编辑角色"),  # type: ignore
                dict(code="manage.role.delete", description="删除角色"),  # type: ignore
                dict(code="manage.role.batchDelete", description="批量删除角色"),  # type: ignore
            ],
        ),
    ]

    session.add_all(user_menus)
    session.commit()


def user(session: Session) -> None:
    """
    默认用户
    :param session:
    :return:
    """

    users: list[UserTable] = [
        UserTable(
            name="超级管理员",
            username="SupperAdmin",
            email="admin@criminal.cn",
            mobile="18888888888",
            password=hash_password("criminal666"),
            isAdmin=True,
        )
    ]

    session.add_all(users)
    session.commit()


def manage(session: Session) -> None:
    """
    系统管理相关的默认数据, 用于初始化数据库
    :param session:
    :return:
    """

    menu(session)
    user(session)
