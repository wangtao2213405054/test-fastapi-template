
from src.schemas import CustomModel

from fastapi import Body
from pydantic import Field, field_validator

import re


class JWTData(CustomModel):
    """ Token解析后的数据 """
    user_id: int = Field(alias="sub")
    is_admin: bool = False


class AuthLoginRequest(CustomModel):
    username: str = Body(..., description="用户名", min_length=6, max_length=128)
    password: str = Body(..., description="密码", min_length=6, max_length=128)


class AccessTokenResponse(CustomModel):
    accessToken: str
    refreshToken: str


STRONG_PASSWORD_PATTERN = re.compile(r"^(?=.*[\d])(?=.*[!@#$%^&*])[\w!@#$%^&*]{6,128}$")


# class AuthUser(CustomModel):
#     email: EmailStr
#     password: str = Field(min_length=6, max_length=128)
#
#     @classmethod
#     @field_validator("password", mode="after")
#     def valid_password(cls, password: str) -> str:
#         if not re.match(STRONG_PASSWORD_PATTERN, password):
#             raise ValueError(
#                 "Password must contain at least "
#                 "one lower character, "
#                 "one upper character, "
#                 "digit or "
#                 "special symbol"
#             )
#
#         return password
