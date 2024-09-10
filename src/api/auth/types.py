# _author: Coke
# _date: 2024/8/22 下午5:00
# _description: 用户认证请求体

from fastapi import Body
from pydantic import EmailStr, Field

from src.models.types import CustomModel


class JWTData(CustomModel):
    """Token解析后的数据"""

    userId: int | None = Field(alias="sub")


class JWTRefreshTokenData(CustomModel):
    """Refresh Token 解析后的数据"""

    userId: int | None = Field(alias="sub")
    uuid: str


class AuthLoginRequest(CustomModel):
    """登录的请求体"""

    username: EmailStr = Body(..., description="用户名", min_length=6, max_length=128)
    password: str = Body(..., description="密码")


class RefreshTokenRequest(CustomModel):
    """刷新 Token 请求体"""

    refreshToken: str
