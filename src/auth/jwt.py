from datetime import timedelta
import datetime
from typing import Any

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from src.auth.config import auth_config
from src.auth.exceptions import AuthorizationFailed, AuthRequired, InvalidToken
from src.auth.schemas import JWTData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/users/tokens", auto_error=False)


def create_access_token(
    *,
    user: dict[str, Any],
    expires_delta: timedelta = timedelta(minutes=auth_config.JWT_EXP),
) -> str:
    """
    创建用户 Token
    :param user: 用户信息
    :param expires_delta: Token 有效期
    :return: Token
    """
    jwt_data = {
        "sub": str(user.get("id")),
        "exp": datetime.datetime.now(datetime.UTC) + expires_delta,
        "is_admin": user["is_admin"],
    }

    return jwt.encode(jwt_data, auth_config.JWT_SECRET, algorithm=auth_config.JWT_ALG)


async def parse_jwt_user_data_optional(
    token: str = Depends(oauth2_scheme),
) -> JWTData | None:
    """
    解析用户 Token 并返回解析后的信息对象
    :param token: 需要解析的 Token
    :return:
    """
    if not token:
        return None

    try:
        payload = jwt.decode(
            token, auth_config.JWT_SECRET, algorithms=[auth_config.JWT_ALG]
        )
    except JWTError:
        raise InvalidToken()

    return JWTData(**payload)


async def parse_jwt_user_data(
    token: JWTData | None = Depends(parse_jwt_user_data_optional),
) -> JWTData:
    """
    解析 JWT 用户信息
    :param token: 需要解析的 Token
    :return:
    """
    if not token:
        raise AuthRequired()

    return token


async def parse_jwt_admin_data(
    token: JWTData = Depends(parse_jwt_user_data),
) -> JWTData:
    """
    解析 JWT 管理员信息
    :param token: 需要解析的 Token
    :return:
    """
    if not token.is_admin:
        raise AuthorizationFailed()

    return token


async def validate_admin_access(
    token: JWTData | None = Depends(parse_jwt_user_data_optional),
) -> None:
    """
    验证管理员访问权限
    :param token: 需要解析的 Token
    :return:
    """
    if token and token.is_admin:
        return

    raise AuthorizationFailed()
