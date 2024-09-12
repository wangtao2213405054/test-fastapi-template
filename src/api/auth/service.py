# _author: Coke
# _date: 2024/8/26 下午3:51
# _description: 用户认证相关逻辑

import datetime
import logging
import uuid
from typing import Annotated

from fastapi import Depends
from sqlmodel import select

from src import cache, database
from src.api.auth import jwt
from src.api.manage.models import UserResponse, UserTable
from src.models.types import RedisData
from src.utils import validate

from .config import PRIVATE_KEY, PUBLIC_KEY, auth_config
from .exceptions import InvalidPassword, InvalidUsername, RefreshTokenNotValid, StandardsPassword, WrongPassword
from .models import AccessTokenResponse
from .security import check_password, decrypt_message, serialize_key
from .types import JWTData, JWTRefreshTokenData

REDIS_REFRESH_KEY = "REFRESH_UUID"


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
    user = await database.select(select(UserTable).where(UserTable.email == username), nullable=True)

    if not user:
        raise InvalidUsername()

    if not check_password(password, user.password):
        raise WrongPassword()

    return user


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

    token_user_info = JWTData(userId=user.id)
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

    _refresh_token = await jwt.parse_jwt_refresh_token(token=token)

    redis_key = await cache.get_by_key(key=get_refresh_key(_refresh_token.userId))

    if redis_key != _refresh_token.uuid:
        raise RefreshTokenNotValid()

    user = await database.select(select(UserTable).where(UserTable.id == _refresh_token.userId))

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


async def get_current_user_table(user_data: Annotated[JWTData, Depends(jwt.parse_jwt_user_data)]) -> UserTable:
    """
    获取当前用户信息

    该函数根据 JWT 数据中的用户 ID 从数据库中获取用户信息。

    :param user_data: 由 JWT 解析函数提供的用户数据
    :return:
    """

    user = await database.select(
        select(UserTable).options(database.joined_load(UserTable.role)).where(UserTable.id == user_data.userId)
    )

    return user


async def get_current_user(
    user: Annotated[UserTable, Depends(get_current_user_table)],
) -> UserResponse:
    """
    获取当前用户响应信息

    :param user: 由 JWT 解析函数提供的用户数据
    :return: 当前用户的响应对象
    """

    roles = user.role.buttonCodes if user.role else []
    return UserResponse(**user.model_dump(), roles=roles)
