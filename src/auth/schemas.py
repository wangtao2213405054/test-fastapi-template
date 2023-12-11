
from src.models import CustomModel, ResponseModel

from fastapi import Body
from pydantic import Field


class JWTData(CustomModel):
    """ Token解析后的数据 """
    user_id: int = Field(alias="sub")
    is_admin: bool = False


class AuthLoginRequest(CustomModel):
    username: str = Body(..., description="用户名", min_length=6, max_length=128)
    password: str = Body(..., description="密码", min_length=6, max_length=128)


class AccessTokenResponse(CustomModel):
    token: str
    refreshToken: str


class AuthLoginResponse(ResponseModel):
    data: AccessTokenResponse
