# _author: Coke
# _date: 2024/7/26 14:20
# _description: Token 相关

import datetime
from typing import Annotated

from authlib.jose import jwt
from authlib.jose.errors import JoseError
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select

from src import database
from src.api.auth.config import auth_config
from src.api.auth.exceptions import AuthorizationFailed, AuthRequired, InvalidToken, RefreshTokenNotValid
from src.api.manage.models import UserTable
from src.config import settings

from .types import JWTData, JWTRefreshTokenData

# OAuth2PasswordBearer 实例，用于从请求中提取 JWT Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.PREFIX}/auth/swaggerLogin", auto_error=False)

HEADER = dict(alg=auth_config.JWT_ALG, typ="JWT")


def create_access_token(
    *,
    user: JWTData,
    expires_delta: datetime.timedelta = datetime.timedelta(minutes=auth_config.ACCESS_TOKEN_EXP),
) -> str:
    """
    创建并生成一个访问令牌 (Access Token)。

    :param user: 包含用户信息的字典，通常包含用户的 ID 和其他必要的数据。
    :param expires_delta: 令牌的有效期，默认为配置中指定的有效期。
    :return: 生成的 JWT 访问令牌字符串。
    """

    payload = dict(
        sub=str(user.userId),
        exp=datetime.datetime.now(datetime.UTC) + expires_delta,
    )

    return jwt.encode(header=HEADER, payload=payload, key=auth_config.ACCESS_TOKEN_KEY).decode("utf-8")


def create_refresh_token(
    *,
    user: JWTRefreshTokenData,
    expires_delta: datetime.timedelta = datetime.timedelta(minutes=auth_config.REFRESH_TOKEN_EXP),
) -> str:
    """
    创建并生成一个刷新令牌 (Refresh Token)。

    :param user: 包含用户信息的字典，通常包含用户的 ID 和其他必要的数据。
    :param expires_delta: 刷新令牌的有效期，默认为配置中指定的有效期。
    :return: 生成的 JWT 刷新令牌字符串。
    """

    payload = dict(
        sub=str(user.userId),
        exp=datetime.datetime.now(datetime.UTC) + expires_delta,
        uuid=str(user.uuid),
    )

    return jwt.encode(header=HEADER, payload=payload, key=auth_config.REFRESH_TOKEN_KEY).decode("utf-8")


async def parse_jwt_refresh_token(token: str) -> JWTRefreshTokenData:
    """
    解析 JWT 刷新令牌并返回解码后的刷新数据。

    :param token:
    :return: 解码后的 JWTRefreshTokenData 数据对象。 如果令牌无效或解析失败，则抛出 RefreshTokenNotValid 异常。
    :raises RefreshTokenNotValid: 当令牌无效、过期或无法解码时。
    """

    try:
        payload = jwt.decode(token, auth_config.REFRESH_TOKEN_KEY)
    except JoseError:
        raise RefreshTokenNotValid()

    return JWTRefreshTokenData(**payload)


async def parse_jwt_user_data_optional(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> JWTData | None:
    """
    解析 JWT 访问令牌并返回解码后的用户数据。

    :param token: 从请求中提取的 JWT 令牌字符串。如果令牌不存在，将返回 None。
    :return: 解码后的 JWT 数据对象。如果令牌无效或解析失败，则抛出 InvalidToken 异常。
    :raises InvalidToken: 当令牌无效、过期或无法解码时。
    """
    if not token:
        return None

    try:
        payload = jwt.decode(token, auth_config.ACCESS_TOKEN_KEY)
    except JoseError:
        raise InvalidToken()

    return JWTData(**payload)


async def parse_jwt_user_data(
    token: Annotated[JWTData, Depends(parse_jwt_user_data_optional)],
) -> JWTData:
    """
    验证并返回解码后的 JWT 用户数据。

    :param token: 解码后的 JWT 数据对象。必须存在并且有效，否则会抛出 AuthRequired 异常。
    :return: 解码后的 JWT 数据对象。
    :raises AuthRequired: 当用户数据无效或未提供时。
    """
    if not token:
        raise AuthRequired()

    return token


async def validate_permission(
    token: Annotated[JWTData, Depends(parse_jwt_user_data)],
    request: Request,
) -> None:
    """
    验证用户访问权限。

    由于继承了 parse_jwt_user_data 函数，会优先对用户的 Token 进行校验。

    校验逻辑: 如果用户不是管理员并且没有绑定角色信息或角色无此接口配置则抛出 AuthorizationFailed 异常。

    :param token: 解码后的 JWT 数据对象。
    :param request: 当前请求的对象
    :return:
    :raises AuthorizationFailed: 当用户不是管理员、无绑定角色信息或权限不足时。
    """

    uri = request.url.path.replace(settings.PREFIX, "")

    user = await database.select(
        select(UserTable).options(database.joined_load(UserTable.role)).where(UserTable.id == token.userId)
    )

    if not (user.isAdmin or (user.roleId and user.role and uri in user.role.menuIds)):
        raise AuthorizationFailed()
