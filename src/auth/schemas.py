
from src.schemas import CustomModel

from fastapi import Body
from fastapi.exceptions import RequestValidationError

from pydantic import Field, field_validator

import re


STRONG_PASSWORD_PATTERN = re.compile(r"^(?=.*[\d])(?=.*[!@#$%^&*])[\w!@#$%^&*]{6,128}$")


class JWTData(CustomModel):
    """ Token解析后的数据 """
    user_id: int = Field(alias="sub")
    is_admin: bool = False


class AuthLoginRequest(CustomModel):
    username: str = Body(..., description="用户名", min_length=6, max_length=128)
    password: str = Body(..., description="密码", min_length=6, max_length=128)

    @field_validator("password", mode="after")
    def valid_password(cls, password: str) -> str:
        if not re.match(STRONG_PASSWORD_PATTERN, password):
            raise RequestValidationError("密码必须至少包含一个小写字母、一个大写字母、数字和特殊符号")

        return password


class AccessTokenResponse(CustomModel):
    accessToken: str
    refreshToken: str
