
from fastapi import Body
import re

from pydantic import Field, field_validator, EmailStr
from sqlmodel import select

from src.schemas import CustomModel
from src.database import fetch_one
from src.auth.models import MenuBase, MenuTable


STRONG_PASSWORD_PATTERN = re.compile(r"^(?=.*\d)(?=.*[!@#$%^&*])[\w!@#$%^&*]{6,128}$")


class JWTData(CustomModel):
    """ Token解析后的数据 """
    user_id: int = Field(alias="sub")
    is_admin: bool = False


class AuthLoginRequest(CustomModel):
    username: EmailStr = Body(..., description="用户名", min_length=6, max_length=128)
    password: str = Body(..., description="密码", min_length=6, max_length=128)

    # noinspection PyNestedDecorators
    @field_validator("password", mode="after")
    @classmethod
    def valid_password(cls, password: str) -> str:
        if not re.match(STRONG_PASSWORD_PATTERN, password):
            raise ValueError("密码必须至少包含一个小写字母、一个大写字母、数字和特殊符号")

        return password


class AccessTokenResponse(CustomModel):
    accessToken: str
    refreshToken: str


class AuthGetMenuRequest(CustomModel):
    nodeId: int = Body(None, description="节点ID")
    keyword: str = Body("", description="关键字查询")


class AuthAddMenuRequest(CustomModel):
    id: int | None = Body(None, description="菜单ID")
    name: str = Body(..., description="菜单名称")
    identifier: str = Body(..., description="菜单标识符")
    nodeId: int = Body(0, description="所属节点ID")
