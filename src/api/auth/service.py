# _author: Coke
# _date: 2024/7/26 14:20
# _description: Auth 验证相关的服务器业务逻辑

from fastapi import Depends
from typing import Annotated

from sqlmodel import select, or_

from src import utils
from src.utils import validate
from src.database import (
    insert_one,
    fetch_all,
    update_one,
    select_one,
    fetch_page,
    delete_one,
    like,
    UniqueDetails,
    unique_check,
)

from .models.types import JWTData
from .config import auth_config
from .jwt import parse_jwt_user_data
from .exceptions import (
    InvalidPassword,
    StandardsPassword,
    WrongPassword,
    InvalidUsername,
)
from .security import serialize_key, decrypt_message, hash_password, check_password
from .models.models import (
    UserTable,
    UserResponse,
    UserCreate,
    MenuTable,
    MenuCreate,
    MenuListResponse,
    MenuInfoResponse,
    RoleTable,
    RoleCreate,
    RoleInfoResponse,
    AffiliationTable,
    AffiliationCreate,
    AffiliationListResponse,
    AffiliationInfoResponse,
)

import logging


def get_public_key() -> str:
    """
    返回当前服务的公钥

    :return:
    """
    public_key_pem = serialize_key(auth_config.PUBLIC_KEY, is_private=False)

    return public_key_pem.decode("utf-8")


def decrypt_password(password: str) -> str:
    """
    对传递过来的密码进行 RSA 解密
    如果处理失败抛出 <InvalidPassword> or <StandardsPassword> 错误

    :param password: 加密的密码
    :return:
    """
    try:
        decrypt_password = decrypt_message(auth_config.PRIVATE_KEY, password)

    except Exception as e:
        logging.error(e)
        raise InvalidPassword()

    verify_password = validate.password(decrypt_password)
    if not verify_password:
        raise StandardsPassword()

    return decrypt_password


@unique_check(
    UserTable,
    mobile=UniqueDetails(message="手机已号存在"),
    email=UniqueDetails(message="邮件已存在"),
)
async def create_user(
    *,
    name: str,
    email: str,
    mobile: str,
    password: str,
    affiliation_id: int,
    avatar: str = None,
    role_id: int = None,
) -> UserResponse:
    """
    创建 一个新的用户

    :param name: 用户名称
    :param email: 用户游戏
    :param mobile: 用户手机号
    :param password: 用户密码
    :param avatar: 头像
    :param role_id: 角色ID
    :param affiliation_id: 所属关系ID
    :return:
    """

    username = utils.pinyin(name)
    password = hash_password(decrypt_password(password))

    user = await insert_one(
        UserTable,
        UserCreate(
            name=name,
            username=username,
            email=email,
            mobile=mobile,
            password=password,
            avatarUrl=avatar,
            roleId=role_id,
            affiliationId=affiliation_id,
        ),
    )

    return user


@unique_check(
    UserTable,
    func_key="user_id",
    model_key="id",
    mobile=UniqueDetails(message="手机已号存在"),
    email=UniqueDetails(message="邮件已存在"),
)
async def update_user(
    *,
    user_id: int,
    name: str,
    email: str,
    mobile: str,
    affiliation_id: int,
    status: bool = True,
    avatar: str = None,
    role_id: int = None,
) -> UserResponse:
    """
    修改用户信息

    :param user_id: 用户ID
    :param name: 用户名称
    :param email: 用户邮箱
    :param mobile: 手机号
    :param affiliation_id: 所属关系ID
    :param status: 在职状态
    :param avatar: 头像
    :param role_id: 角色ID
    :return:
    """
    user: UserTable = await select_one(select(UserTable).where(UserTable.id == user_id))
    user.name = name
    user.username = utils.pinyin(name)
    user.email = email
    user.mobile = mobile
    user.avatarUrl = avatar
    user.status = status
    user.roleId = role_id
    user.affiliationId = affiliation_id

    return await update_one(user)


async def authenticate_user(username: str, password: str) -> UserResponse:
    """
    验证用户密码
    :param username: 用户名
    :param password: 密码
    :return:
    """
    user: UserResponse = await select_one(select(UserTable).where(UserTable.email == username))

    if not user:
        raise InvalidUsername()

    if not check_password(password, user.password):
        raise WrongPassword()

    return user


async def get_current_user(user_data: Annotated[JWTData, Depends(parse_jwt_user_data)]) -> UserResponse:
    """
    获取当前用户信息
    示例: user: Annotated[UserResponse, Depends(get_current_user)]

    :param user_data: 传递的 Token
    :return:
    """

    return await select_one(select(UserTable).where(UserTable.id == user_data.userId))


async def update_password(*, user_id: int, old_password: str, new_password: str) -> None:
    """
    更新用户的密码信息

    :param user_id: 用户ID
    :param old_password: 旧密码
    :param new_password: 新的密码
    :return:
    """
    old_password = decrypt_password(old_password)
    new_password = hash_password(decrypt_password(new_password))
    user: UserTable = await select_one(select(UserTable).where(UserTable.id == user_id))

    verify_password = check_password(old_password, user.password)
    if not verify_password:
        raise WrongPassword()

    user.password = new_password
    await update_one(user)


async def edit_affiliation(*, affiliation_id: int, name: str, node_id: int) -> AffiliationInfoResponse:
    """
    创建/更新 一个所属关系

    :param affiliation_id: 所属关系ID 如何为真则视为修改
    :param name: 所属关系名称
    :param node_id: 节点ID
    :return:
    """
    if affiliation_id:
        affiliation: AffiliationInfoResponse = await select_one(
            select(AffiliationTable).where(AffiliationTable.id == affiliation_id)
        )
        affiliation.name = name
        affiliation.nodeId = node_id
        return await update_one(affiliation)

    return await insert_one(AffiliationTable, AffiliationCreate(name=name, nodeId=node_id))


async def delete_affiliation(*, affiliation_id) -> AffiliationInfoResponse:
    """
    删除一个所属关系

    :param affiliation_id: 所属关系ID
    :return:
    """
    return await delete_one(select(AffiliationTable).where(AffiliationTable.id == affiliation_id))


async def get_affiliation_tree(*, node_id: int, keyword: str = "") -> list[AffiliationListResponse]:
    """
    获取当前的所属关系树

    :param node_id: 节点ID
    :param keyword: 关键字查询
    :return:
    """
    affiliation_dict_list: list[AffiliationListResponse] = []

    affiliation_list: list[AffiliationInfoResponse] = await fetch_all(
        select(AffiliationTable).where(
            AffiliationTable.nodeId == node_id,
            like(field=AffiliationTable.name, keyword=keyword),
        )
    )

    for item in affiliation_list:
        children = await get_affiliation_tree(node_id=item.id)
        items = AffiliationListResponse(children=children, **item.model_dump())
        affiliation_dict_list.append(items)

    return affiliation_dict_list


async def edit_menu(*, menu_id: int, name: str, identifier: str, node_id: int) -> MenuInfoResponse:
    """
    创建/更新 一个权限菜单

    :param menu_id: 权限菜单ID 如何为真则视为修改
    :param name: 菜单名称
    :param identifier: 菜单标识符
    :param node_id: 节点ID
    :return:
    """
    # 修改
    if menu_id:
        menu: MenuInfoResponse = await select_one(select(MenuTable).where(MenuTable.id == menu_id))
        menu.name = name
        menu.identifier = identifier
        menu.nodeId = node_id
        return await update_one(menu)

    return await insert_one(MenuTable, MenuCreate(name=name, identifier=identifier, nodeId=node_id))


async def delete_menu(*, menu_id: int) -> MenuInfoResponse:
    """
    删除一个权限菜单

    :param menu_id: 权限菜单ID
    :return:
    """
    return await delete_one(select(MenuTable).where(MenuTable.id == menu_id))


async def get_menu_tree(*, node_id: int, keyword: str = "") -> list[MenuListResponse]:
    """
    递归遍历所有子菜单信息

    :param node_id: 开始节点
    :param keyword: 关键字匹配
    :return:
    """
    menu_dict_list: list[MenuListResponse] = []

    menu_list: list[MenuInfoResponse] = await fetch_all(
        select(MenuTable).where(
            MenuTable.nodeId == node_id,
            or_(
                like(field=MenuTable.name, keyword=keyword),
                like(field=MenuTable.identifier, keyword=keyword),
            ),
        )
    )

    for item in menu_list:
        children = await get_menu_tree(node_id=item.id)
        items = MenuListResponse(children=children, **item.model_dump())
        menu_dict_list.append(items)

    return menu_dict_list


async def edit_role(*, role_id: int, name: str, identifier: str, identifier_list: list[str]) -> RoleInfoResponse:
    """
    创建/修改 一个角色信息

    :param role_id: 角色ID
    :param name: 角色名称
    :param identifier: 角色标识符
    :param identifier_list: 此角色绑定的权限菜单
    :return:
    """

    if role_id:
        role: RoleInfoResponse = await select_one(select(RoleTable).where(RoleTable.id == role_id))
        role.name = name
        role.identifier = identifier
        role.identifierList = identifier_list
        return await update_one(role)

    return await insert_one(
        RoleTable,
        RoleCreate(name=name, identifier=identifier, identifier_list=identifier_list),
    )


async def get_role_list(page: int, size: int, *, keyword: str = "") -> list[RoleInfoResponse]:
    """
    获取角色信息列表

    :param page: 当前页
    :param size: 当前页大小
    :param keyword: 关键字查询, name or identifier
    :return:
    """

    return await fetch_page(
        select(RoleTable).where(
            or_(
                like(field=RoleTable.name, keyword=keyword),
                like(field=RoleTable.identifier, keyword=keyword),
            )
        ),
        page=page,
        size=size,
    )


async def delete_role(*, role_id: int) -> RoleInfoResponse:
    """
    删除一个角色信息

    :param role_id: 角色信息ID
    :return:
    """

    return await delete_one(select(RoleTable).where(RoleTable.id == role_id))
