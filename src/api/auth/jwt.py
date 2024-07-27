# _author: Coke
# _date: 2024/7/27 21:24
# _description: JWT Token 令牌

from typing import Any, Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from src.api.auth.config import auth_config
from src.config import settings
from src.api.auth.exceptions import AuthorizationFailed, AuthRequired, InvalidToken
from .models.types import JWTData

import datetime
import uuid

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.PREFIX}/auth/swagger/login", auto_error=False)


def create_access_token(
    *,
    user: dict[str, Any],
    expires_delta: datetime.timedelta = datetime.timedelta(minutes=auth_config.ACCESS_TOKEN_EXP)
) -> str:
    """
    创建用户 Token

    :param user: 用户信息
    :param expires_delta: Token 有效期
    :return: Token
    """

    jwt_data = dict(
        sub=str(user.get("id")),
        exp=datetime.datetime.now(datetime.UTC) + expires_delta,
    )

    return jwt.encode(jwt_data, auth_config.ACCESS_TOKEN_KEY, algorithm=auth_config.JWT_ALG)


def create_refresh_token(
    *,
    user: dict[str, Any],
    expires_delta: datetime.timedelta = datetime.timedelta(minutes=auth_config.REFRESH_TOKEN_EXP)
) -> str:
    """
    创建 Refresh Token

    :param user: 用户信息
    :param expires_delta: 有效期
    :return:
    """

    jwt_data = dict(
        sub=str(user.get("id")),
        exp=datetime.datetime.now(datetime.UTC) + expires_delta,
        uuid=str(uuid.uuid4()),
    )
    return jwt.encode(jwt_data, auth_config.REFRESH_TOKEN_KEY, algorithm=auth_config.JWT_ALG)


async def parse_jwt_user_data_optional(token: Annotated[str, Depends(oauth2_scheme)]) -> JWTData | None:
    """
    解析用户 Token 并返回解析后的信息对象

    :param token: 需要解析的 Token
    :return:
    """
    if not token:
        return None

    try:
        payload = jwt.decode(
            token, auth_config.ACCESS_TOKEN_KEY, algorithms=[auth_config.JWT_ALG]
        )
    except JWTError:
        raise InvalidToken()

    return JWTData(**payload)


async def parse_jwt_user_data(token: Annotated[JWTData, Depends(parse_jwt_user_data_optional)]) -> JWTData:
    """
    身份验证

    :param token: 需要解析的 Token
    :return:
    """
    if not token:
        raise AuthRequired()

    return token


async def parse_jwt_admin_data(token: Annotated[JWTData, Depends(parse_jwt_user_data)]) -> JWTData:
    """
    解析 JWT 管理员信息

    :param token: 需要解析的 Token
    :return:
    """
    if not token.is_admin:
        raise AuthorizationFailed()

    return token


async def validate_admin_access(token: Annotated[JWTData, Depends(parse_jwt_user_data_optional)]) -> None:
    """
    验证管理员访问权限

    :param token: 需要解析的 Token
    :return:
    """
    if token and token.is_admin:
        return

    raise AuthorizationFailed()
