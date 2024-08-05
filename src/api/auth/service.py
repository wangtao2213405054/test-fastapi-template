# _author: Coke
# _date: 2024/7/26 14:20
# _description: Auth 验证相关的服务器业务逻辑

import asyncio
import datetime
import logging
import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.sql.elements import ColumnElement
from sqlmodel import or_, select

from src import cache, database, utils
from src.api.auth import jwt
from src.models.types import RedisData
from src.utils import validate

from .config import PRIVATE_KEY, PUBLIC_KEY, auth_config
from .exceptions import InvalidPassword, InvalidUsername, RefreshTokenNotValid, StandardsPassword, WrongPassword
from .jwt import parse_jwt_refresh_token, parse_jwt_user_data
from .models.models import (
    AffiliationCreate,
    AffiliationInfoResponse,
    AffiliationListResponse,
    AffiliationTable,
    MenuCreate,
    MenuInfoResponse,
    MenuListResponse,
    MenuTable,
    RoleCreate,
    RoleInfoResponse,
    RoleTable,
    UserCreate,
    UserResponse,
    UserTable,
)
from .models.types import AccessTokenResponse, JWTData, JWTRefreshTokenData
from .security import check_password, decrypt_message, hash_password, serialize_key

REDIS_REFRESH_KEY = "REFRESH_UUID"


def get_refresh_key(user_id: int | None) -> str:
    """
    获取刷新令牌的 Redis Key

    :param user_id: 用户ID
    :return: Redis 查询 刷新令牌的 Key
    """
    return f"{REDIS_REFRESH_KEY}_{user_id}"


def get_public_key() -> str:
    """
    返回当前服务的公钥

    该函数序列化并返回当前服务的公钥，以 PEM 格式编码为字符串。

    :return: 公钥的 PEM 格式字符串
    """
    public_key_pem = serialize_key(PUBLIC_KEY)
    return public_key_pem.decode("utf-8")


async def login(username: str, password: str) -> AccessTokenResponse:
    """
    用户登录并生成用户访问令牌

    :param username: 用户名(邮箱)
    :param password: 密码
    :return: Token and Refresh Token
    """

    password_decrypt = decrypt_password(password)
    user = await authenticate_user(username, password_decrypt)

    response = await create_token(user)

    return response


async def create_token(user: UserTable) -> AccessTokenResponse:
    """
    创建用户访问令牌

    生成访问令牌并将 Refresh Token 中的 uuid 存储到 Redis

    :param user: 用户信息对象
    :return: Token and Refresh Token
    """

    token_user_info = JWTData(userId=user.id, isAdmin=user.isAdmin)
    token = jwt.create_access_token(user=token_user_info)

    _uuid = str(uuid.uuid4())
    expires_delta: datetime.timedelta = datetime.timedelta(minutes=auth_config.REFRESH_TOKEN_EXP)
    refresh_user_info = JWTRefreshTokenData(userId=user.id, uuid=_uuid)
    _refresh_token = jwt.create_refresh_token(user=refresh_user_info, expires_delta=expires_delta)

    redis_value = RedisData(key=get_refresh_key(user.id), value=_uuid, ttl=expires_delta)
    await cache.set_redis_key(redis_value)

    return AccessTokenResponse(accessToken=token, refreshToken=_refresh_token)


async def refresh_token(token: str) -> AccessTokenResponse:
    """
    通过刷新令牌获取新的 Access Token 和 Refresh Token

    :param token: 刷新令牌
    :return: Token and Refresh Token
    :raises RefreshTokenNotValid: 当令牌无效、过期、和缓存不匹配或无法解码时。
    """

    _refresh_token = await parse_jwt_refresh_token(token=token)

    redis_key = await cache.get_by_key(key=get_refresh_key(_refresh_token.userId))

    if redis_key != _refresh_token.uuid:
        raise RefreshTokenNotValid()

    user: UserTable = await database.select(select(UserTable).where(UserTable.id == _refresh_token.userId))
    response = await create_token(user)

    return response


def decrypt_password(password: str) -> str:
    """
    对传递过来的密码进行 RSA 解密
    如果处理失败抛出 <InvalidPassword> 或 <StandardsPassword> 错误

    该函数使用 RSA 私钥解密传递的加密密码，并验证其符合标准。如果解密或验证失败，则抛出适当的异常。

    :param password: 加密的密码
    :return: 解密后的密码
    :raises InvalidPassword: 解密失败时抛出
    :raises StandardsPassword: 密码不符合标准时抛出
    """
    try:
        rsa_password = decrypt_message(PRIVATE_KEY, password)
    except Exception as e:
        logging.error(e)
        raise InvalidPassword()

    verify_password = validate.password(rsa_password)
    if not verify_password:
        raise StandardsPassword()

    return rsa_password


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

    user: UserResponse = await database.insert(
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

    return user


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
    user: UserTable = await database.select(select(UserTable).where(UserTable.id == user_id), nullable=False)
    user.name = name
    user.username = utils.pinyin(name)
    user.email = email
    user.mobile = mobile
    user.avatarUrl = avatar
    user.status = status
    user.roleId = role_id
    user.affiliationId = affiliation_id

    return await database.update(user)


async def authenticate_user(username: str, password: str) -> UserTable:
    """
    验证用户密码

    该函数验证给定的用户名和密码是否匹配。如果用户名不存在或密码错误，则抛出适当的异常。

    :param username: 用户名（通常是邮箱）
    :param password: 密码
    :return: 用户响应对象
    :raises InvalidUsername: 用户名不存在时抛出
    :raises WrongPassword: 密码错误时抛出
    """
    user: UserTable = await database.select(select(UserTable).where(UserTable.email == username))

    if not user:
        raise InvalidUsername()

    if not check_password(password, user.password):
        raise WrongPassword()

    return user


async def get_current_user(
    user_data: Annotated[JWTData, Depends(parse_jwt_user_data)],
) -> UserResponse:
    """
    获取当前用户信息

    该函数根据 JWT 数据中的用户 ID 从数据库中获取用户信息。

    :param user_data: 由 JWT 解析函数提供的用户数据
    :return: 当前用户的响应对象
    """
    return await database.select(select(UserTable).where(UserTable.id == user_data.userId))


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
    user: UserTable = await database.select(select(UserTable).where(UserTable.id == user_id))

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
        affiliation: AffiliationInfoResponse = await database.select(
            select(AffiliationTable).where(AffiliationTable.id == affiliation_id)
        )
        affiliation.name = name
        affiliation.nodeId = node_id
        return await database.update(affiliation)

    return await database.insert(AffiliationTable, AffiliationCreate(name=name, nodeId=node_id))


async def delete_affiliation(*, affiliation_id: int) -> AffiliationInfoResponse:
    """
    删除一个所属关系

    该函数根据 `affiliation_id` 删除指定的所属关系。

    :param affiliation_id: 所属关系 ID
    :return: 删除的所属关系的响应对象
    """
    return await database.delete(select(AffiliationTable).where(AffiliationTable.id == affiliation_id))


async def get_affiliation_tree(*, node_id: int, keyword: str = "") -> list[AffiliationListResponse]:
    """
    获取当前的所属关系树

    递归地获取从指定节点开始的所有所属关系，并根据 `keyword` 进行关键字匹配。

    :param node_id: 节点 ID
    :param keyword: 关键字查询（可选）
    :return: 所有所属关系的列表
    """
    affiliation_dict_list: list[AffiliationListResponse] = []

    clause: list[ColumnElement[bool] | bool] = [database.like(field=AffiliationTable.name, keyword=keyword)]

    if node_id or not keyword:
        clause.append(AffiliationTable.nodeId == node_id)

    query = select(AffiliationTable).where(*clause)
    affiliation_list: list[AffiliationInfoResponse] = await database.select_all(query)

    tasks = [get_affiliation_tree(node_id=item.id, keyword=keyword) for item in affiliation_list]
    children_list = await asyncio.gather(*tasks)

    for item, children in zip(affiliation_list, children_list):
        affiliation_dict_list.append(AffiliationListResponse(children=children, **item.model_dump()))

    return affiliation_dict_list


@database.unique_check(
    MenuTable,
    func_key="menu_id",
    model_key="id",
    identifier=database.UniqueDetails(message="标识符"),
)
async def edit_menu(*, menu_id: int, name: str, identifier: str, node_id: int) -> MenuInfoResponse:
    """
    创建/更新一个权限菜单

    该函数根据 `menu_id` 判断是创建新的权限菜单还是更新现有的菜单。

    :param menu_id: 权限菜单 ID（如果提供，则视为更新）
    :param name: 菜单名称
    :param identifier: 菜单标识符
    :param node_id: 节点 ID
    :return: 权限菜单的响应对象
    """
    # 修改
    if menu_id:
        menu: MenuInfoResponse = await database.select(select(MenuTable).where(MenuTable.id == menu_id))
        menu.name = name
        menu.identifier = identifier
        menu.nodeId = node_id
        return await database.update(menu)

    return await database.insert(MenuTable, MenuCreate(name=name, identifier=identifier, nodeId=node_id))


async def delete_menu(*, menu_id: int) -> MenuInfoResponse:
    """
    删除一个权限菜单

    该函数根据 `menu_id` 删除指定的权限菜单。

    :param menu_id: 权限菜单 ID
    :return: 删除的权限菜单的响应对象
    """
    return await database.delete(select(MenuTable).where(MenuTable.id == menu_id))


async def get_menu_tree(*, node_id: int, keyword: str = "") -> list[MenuListResponse]:
    """
    递归遍历所有子菜单信息

    该函数递归地获取从指定节点开始的所有子菜单，并根据 `keyword` 进行关键字匹配。

    条件构成:
        - 如果 keyword 不为空，则添加模糊匹配条件。
        - 如果 node_id 不为空，或者 keyword 为空，则添加 node_id 的条件。
        - 如果当 keyword 和 node_id 都为空时，仍需要通过 node_id 进行过滤。

    :param node_id: 开始节点 ID
    :param keyword: 关键字匹配（可选）
    :return: 所有子菜单的列表
    """
    menu_dict_list: list[MenuListResponse] = []

    clause: list[ColumnElement[bool] | bool] = [
        or_(
            database.like(field=MenuTable.name, keyword=f"%{keyword}%"),
            database.like(field=MenuTable.identifier, keyword=f"%{keyword}%"),
        )
    ]

    # 如果 keyword 为空 或 node_id 为真将 node_id 添加入 where 条件
    if node_id or not keyword:
        clause.append(MenuTable.nodeId == node_id)

    # 查询菜单列表
    query = select(MenuTable).where(*clause)
    menu_list: list[MenuInfoResponse] = await database.select_all(query)

    # 并行获取子菜单
    tasks = [get_menu_tree(node_id=item.id, keyword=keyword) for item in menu_list]
    children_list = await asyncio.gather(*tasks)

    # 构建响应列表
    for item, children in zip(menu_list, children_list):
        menu_dict_list.append(MenuListResponse(children=children, **item.model_dump()))

    return menu_dict_list


async def edit_role(*, role_id: int, name: str, describe: str, identifier_list: list[str]) -> RoleInfoResponse:
    """
    创建/修改一个角色信息

    该函数根据 `role_id` 判断是创建新的角色还是更新现有角色的信息。

    :param role_id: 角色 ID（如果提供，则视为更新）
    :param name: 角色名称
    :param describe: 角色描述
    :param identifier_list: 此角色绑定的权限菜单标识符列表
    :return: 角色的响应对象
    """
    if role_id:
        role: RoleInfoResponse = await database.select(select(RoleTable).where(RoleTable.id == role_id), nullable=False)
        role.name = name
        role.describe = describe
        role.identifierList = identifier_list
        return await database.update(role)

    return await database.insert(
        RoleTable,
        RoleCreate(name=name, describe=describe, identifierList=identifier_list),
    )


async def get_role_list(page: int, size: int, *, keyword: str = "") -> list[RoleInfoResponse]:
    """
    获取角色信息列表

    该函数分页获取角色信息，并根据 `keyword` 进行关键字匹配。

    :param page: 当前页
    :param size: 每页的大小
    :param keyword: 关键字查询（可选，匹配角色名称或标识符）
    :return: 角色信息的列表
    """
    return await database.pagination(
        select(RoleTable).where(database.like(field=RoleTable.name, keyword=keyword)),
        page=page,
        size=size,
    )


async def delete_role(*, role_id: int) -> RoleInfoResponse:
    """
    删除一个角色信息

    该函数根据 `role_id` 删除指定的角色信息。

    :param role_id: 角色 ID
    :return: 删除的角色信息的响应对象
    """
    return await database.delete(select(RoleTable).where(RoleTable.id == role_id))
