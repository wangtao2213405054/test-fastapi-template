# _author: Coke
# _date: 2024/7/26 14:20
# _description: 系统管理相关的服务器业务逻辑

from itertools import chain

from sqlalchemy import ColumnElement
from sqlmodel import or_, select

from src import database, utils
from src.api.auth.exceptions import WrongPassword
from src.api.auth.security import check_password, hash_password
from src.api.auth.service import decrypt_password
from src.exceptions import BadData, DatabaseUniqueError
from src.models.types import Pagination

from .models import (
    AffiliationCreate,
    AffiliationInfoResponse,
    AffiliationListResponse,
    AffiliationTable,
    MenuCreate,
    MenuInfoResponse,
    MenuListResponse,
    MenuPermissionTreeResponse,
    MenuSimplifyListResponse,
    MenuTable,
    RoleCreate,
    RoleInfoResponse,
    RoleTable,
    UserCreate,
    UserResponse,
    UserTable,
)
from .types import MENU_ROUTE, PERMISSION_BUTTONS, PERMISSION_INTERFACE, Query, SubPermission


@database.unique_check(
    UserTable,
    mobile=database.UniqueDetails(message="手机号码"),
    email=database.UniqueDetails(message="邮箱"),
)
async def create_user(
    *,
    name: str,
    email: str,
    mobile: str,
    password: str,
    affiliation_id: int,
    avatar: str | None = None,
    role_id: int | None = None,
) -> UserResponse:
    """
    创建一个新的用户

    该函数创建一个新的用户记录，并将其插入数据库。用户的密码经过解密和哈希处理，以确保安全性。

    :param name: 用户名称
    :param email: 用户邮箱
    :param mobile: 用户手机号码
    :param password: 用户密码（加密格式）
    :param affiliation_id: 所属关系 ID
    :param avatar: 用户头像 URL（可选）
    :param role_id: 用户角色 ID（可选）
    :return: 创建的用户响应对象
    """
    username = utils.pinyin(name)
    password_hash: bytes = hash_password(decrypt_password(password))

    user = await database.insert(
        UserTable,
        UserCreate(
            name=name,
            username=username,
            email=email,
            mobile=mobile,
            password=password_hash,
            avatarUrl=avatar,
            roleId=role_id,
            affiliationId=affiliation_id,
        ),
    )

    return UserResponse(**user.model_dump())


@database.unique_check(
    UserTable,
    func_key="user_id",
    model_key="id",
    mobile=database.UniqueDetails(message="手机号码已存在"),
    email=database.UniqueDetails(message="邮件已存在"),
)
async def update_user(
    *,
    user_id: int,
    name: str,
    email: str,
    mobile: str,
    affiliation_id: int,
    status: bool = True,
    avatar: str | None = None,
    role_id: int | None = None,
) -> UserResponse:
    """
    修改用户信息

    该函数更新用户的相关信息，包括姓名、邮箱、手机号码等，并保存到数据库中。

    :param user_id: 用户 ID
    :param name: 用户名称
    :param email: 用户邮箱
    :param mobile: 用户手机号码
    :param affiliation_id: 所属关系 ID
    :param status: 用户状态（默认为在职）
    :param avatar: 用户头像 URL（可选）
    :param role_id: 用户角色 ID（可选）
    :return: 更新后的用户响应对象
    """
    user = await database.select(select(UserTable).where(UserTable.id == user_id))
    user.name = name
    user.username = utils.pinyin(name)
    user.email = email
    user.mobile = mobile
    user.avatarUrl = avatar
    user.status = status
    user.roleId = role_id
    user.affiliationId = affiliation_id

    _update_user = await database.update(user)

    return UserResponse(**_update_user.model_dump())


async def update_password(*, user_id: int, old_password: str, new_password: str) -> None:
    """
    更新用户的密码信息

    该函数验证旧密码是否正确，并将用户的密码更新为新的密码。密码进行解密和哈希处理。

    :param user_id: 用户 ID
    :param old_password: 旧密码
    :param new_password: 新密码
    :return: None
    :raises WrongPassword: 旧密码不正确时抛出
    """
    old_password = decrypt_password(old_password)
    password = hash_password(decrypt_password(new_password))
    user = await database.select(select(UserTable).where(UserTable.id == user_id))

    verify_password = check_password(old_password, user.password)
    if not verify_password:
        raise WrongPassword()

    user.password = password
    await database.update(user)


async def edit_affiliation(*, affiliation_id: int, name: str, node_id: int) -> AffiliationInfoResponse:
    """
    创建/更新一个所属关系

    该函数根据 `affiliation_id` 来判断是创建新的所属关系还是更新现有的所属关系。

    :param affiliation_id: 所属关系 ID（如果提供，则视为更新）
    :param name: 所属关系名称
    :param node_id: 节点 ID
    :return: 所属关系的响应对象
    """
    if affiliation_id:
        affiliation = await database.select(select(AffiliationTable).where(AffiliationTable.id == affiliation_id))
        affiliation.name = name
        affiliation.nodeId = node_id

        update_affiliation = await database.update(affiliation)

        return AffiliationInfoResponse(**update_affiliation.model_dump())

    add_affiliation = await database.insert(AffiliationTable, AffiliationCreate(name=name, nodeId=node_id))

    return AffiliationInfoResponse(**add_affiliation.model_dump())


async def delete_affiliation(*, affiliation_id: int) -> AffiliationInfoResponse:
    """
    删除一个所属关系

    该函数根据 `affiliation_id` 删除指定的所属关系。

    :param affiliation_id: 所属关系 ID
    :return: 删除的所属关系的响应对象
    """
    affiliation = await database.delete(select(AffiliationTable).where(AffiliationTable.id == affiliation_id))

    return AffiliationInfoResponse(**affiliation.model_dump())


async def get_affiliation_tree(*, node_id: int, keyword: str = "") -> list[AffiliationListResponse]:
    """
    获取当前的所属关系树

    递归地获取从指定节点开始的所有所属关系，并根据 `keyword` 进行关键字匹配。

    :param node_id: 节点 ID
    :param keyword: 关键字查询（可选）
    :return: 所有所属关系的列表
    """

    affiliation_dict_list = await database.select_tree(
        AffiliationTable, AffiliationListResponse, node_id=node_id, keyword_map_list=["name"], keyword=keyword
    )

    return affiliation_dict_list  # type: ignore


async def edit_role(
    *,
    role_id: int,
    name: str,
    describe: str | None,
    status: bool,
) -> RoleInfoResponse:
    """
    创建/修改一个角色信息

    该函数根据 `role_id` 判断是创建新的角色还是更新现有角色的信息。

    :param role_id: 角色 ID（如果提供，则视为更新）
    :param name: 角色名称
    :param describe: 角色描述
    :param status: 角色状态
    :return: 角色的响应对象
    """
    if role_id:
        role = await database.select(select(RoleTable).where(RoleTable.id == role_id))
        role.name = name
        role.describe = describe
        role.status = status

        update_role = await database.update(role)
        return RoleInfoResponse(**update_role.model_dump())

    add_role = await database.insert(
        RoleTable,
        RoleCreate(name=name, describe=describe, status=status),
    )
    return RoleInfoResponse(**add_role.model_dump())


async def edit_role_permission(
    *,
    role_id: int,
    menu_ids: list[int] | None = None,
    interface_codes: list[str] | None = None,
    button_codes: list[str] | None = None,
) -> RoleInfoResponse:
    """
    修改一个角色的绑定权限信息

    该函数根据 `role_id` 来修改角色的绑定权限信
    :param role_id: 角色ID
    :param menu_ids: 菜单id列表
    :param interface_codes: 接口code列表
    :param button_codes: 按钮code列表
    :return:
    """
    # 如都为 None 则失败
    if all(param is None for param in [menu_ids, interface_codes, button_codes]):
        raise BadData

    role = await database.select(select(RoleTable).where(RoleTable.id == role_id))

    if menu_ids is not None:
        role.menuIds = menu_ids

    if interface_codes is not None:
        role.interfaceCodes = interface_codes

    if button_codes is not None:
        role.buttonCodes = button_codes

    update_role = await database.update(role)
    return RoleInfoResponse(**update_role.model_dump())


async def get_role_list(
    page: int, size: int, *, keyword: str = "", status: bool | None = None
) -> Pagination[list[RoleInfoResponse]]:
    """
    获取角色信息列表

    该函数分页获取角色信息，并根据 `keyword` 进行关键字匹配。

    :param page: 当前页
    :param size: 每页的大小
    :param keyword: 关键字查询（可选，匹配角色名称或标识符）
    :param status: 角色状态
    :return: 角色信息的列表
    """
    clause: list[ColumnElement[bool] | bool] = [database.like(field=RoleTable.name, keyword=keyword)]

    if status is not None:
        clause.append(RoleTable.status == status)

    role_pagination = await database.pagination(
        select(RoleTable).where(*clause),
        page=page,
        size=size,
    )

    return Pagination(
        page=role_pagination.page,
        pageSize=role_pagination.pageSize,
        records=[RoleInfoResponse(**role.model_dump()) for role in role_pagination.records],
        total=role_pagination.total,
    )


async def delete_role(*, role_id: int) -> RoleInfoResponse:
    """
    删除一个角色信息

    该函数根据 `role_id` 删除指定的角色信息。

    :param role_id: 角色 ID
    :return: 删除的角色信息的响应对象
    """

    role = await database.delete(select(RoleTable).where(RoleTable.id == role_id))
    return RoleInfoResponse(**role.model_dump())


async def batch_delete_role(*, ids: list[int]) -> list[RoleInfoResponse]:
    """
    删除多个角色

    该函数根据 `ids` 删除指定的角色。

    :param ids: 角色 ID 列表
    :return
    """

    role = await database.batch_delete(
        select(RoleTable).where(or_(*[RoleTable.id == _id for _id in ids], *[MenuTable.nodeId == _id for _id in ids]))
    )

    return [RoleInfoResponse(**item.model_dump()) for item in role]


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

    async def check_permissions(permissions: list[SubPermission], menu_type: str, name: str) -> None:
        """检查重复权限和冲突权限"""
        codes = [item.code for item in permissions]

        # 检查重复项
        duplicates = utils.get_duplicates(codes)
        if duplicates:
            raise DatabaseUniqueError(f"`{'、'.join(duplicates)}`{name}权限重复")

        # 检查与数据库中的冲突
        if codes:
            clause = [MenuTable.id != menu_id] if menu_id else None
            permission_list = await get_menu_permission_list(menu_type, clause=clause)
            existing_codes = {item.code for item in permission_list}
            intersection = set(codes) & existing_codes
            if intersection:
                raise DatabaseUniqueError(f"`{'、'.join(intersection)}`{name}权限已存在")

    await check_permissions(buttons, PERMISSION_BUTTONS, "按钮")
    await check_permissions(interfaces, PERMISSION_INTERFACE, "接口")

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


async def get_page_list() -> list[str]:
    """
    获取页面列表

    :return: 页面列表
    """
    menu = await database.select_all(select(MenuTable.routeName).where(MenuTable.menuType == MENU_ROUTE))

    return menu


async def get_menu_simplify_tree() -> list[MenuSimplifyListResponse]:
    """
    获取简化后全部的菜单树列表

    :return: 菜单树列表
    """
    menu = await database.select_tree(
        MenuTable,
        MenuSimplifyListResponse,
        node_id=0,
    )

    return menu  # type: ignore


async def get_menu_permission_list(
    menu_type: str, *, clause: list[ColumnElement[bool]] | list[bool] | None = None
) -> list[SubPermission]:
    """
    根据 `menu_type` 获取路由中全部的权限菜单

    :param menu_type: buttons or interfaces
    :param clause: where 条件
    :return: 权限菜单列表
    """

    if clause is None:
        clause = []

    menu = await database.select_all(select(getattr(MenuTable, menu_type)).where(*clause))

    return [SubPermission(**item) for item in list(chain.from_iterable(menu))]


async def get_menu_permission_tree(menu_type: str) -> list[MenuPermissionTreeResponse]:
    """
    从数据库中检索并转换菜单树为权限树，然后过滤掉任何不活跃的项。

    :param menu_type: buttons or interfaces
    :return:
    """

    def transform_menu_tree_to_permission_tree(
        tree: list[MenuListResponse], depth: int = 1
    ) -> list[MenuPermissionTreeResponse]:
        """
        递归地将菜单树转换为权限树。

        :param tree: 菜单响应对象列表
        :param depth: 递归深度
        :return:
        """
        permission_menu_list = []

        for index, _menu in enumerate(tree, start=1):
            permission_menu = MenuPermissionTreeResponse(
                disabled=True, key=f"{depth}-{index}", label=_menu.menuName, value=_menu.routePath, children=[]
            )

            if _menu.children:
                children = transform_menu_tree_to_permission_tree(_menu.children, depth + 1)
                for _children in children:
                    permission_menu.children.append(_children)

            permission_type = getattr(_menu, menu_type)
            if permission_type:
                for button_index, button in enumerate(permission_type, start=1):
                    permission_menu.children.append(
                        MenuPermissionTreeResponse(
                            disabled=False,
                            key=f"{depth}-{index}-{button_index}",
                            label=button.description,
                            value=button.code,
                        )
                    )

            permission_menu_list.append(permission_menu)

        return permission_menu_list

    def filter_disabled(tree: list[MenuPermissionTreeResponse]) -> list[MenuPermissionTreeResponse]:
        """
        过滤掉树中所有被禁用的项及其子项（如果没有活跃的项存在）。

        :param tree:
        :return:
        """
        # 过滤当前层级的数据
        filtered_children = []
        has_active = False

        for item in tree:
            if item.children:
                # 递归过滤子项
                item.children = filter_disabled(item.children)

            # 检查当前项是否有 active 子项
            if not item.disabled:
                has_active = True

            # 如果当前项或其子项有 active，则保留
            if has_active or item.children:
                filtered_children.append(item)

        return filtered_children

    menu = await database.select_tree(MenuTable, MenuListResponse, node_id=0)

    return filter_disabled(transform_menu_tree_to_permission_tree(menu))  # type: ignore
