# _author: Coke
# _date: 2024/7/25 13:10
# _description: 用户验证相关请求模型

from fastapi import Body
from pydantic import EmailStr, Field, HttpUrl, field_validator

from src.models.types import (
    CustomModel,
    GeneralKeywordPageRequestModel,
    GeneralKeywordRequestModel,
)
from src.utils import validate


class JWTData(CustomModel):
    """Token解析后的数据"""

    userId: int | None = Field(alias="sub")
    isAdmin: bool = False


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


class AccessTokenResponse(RefreshTokenRequest):
    """登录的响应结构"""

    accessToken: str


class SwaggerToken(CustomModel):
    """Swagger 登录的响应结构"""

    access_token: str
    token_type: str


class UserBaseRequest(CustomModel):
    """用户基础请求类"""

    name: str = Body(..., description="用户名称", min_length=2, max_length=128)
    email: EmailStr = Body(..., description="邮箱", min_length=6, max_length=128)
    mobile: str = Body(..., description="手机号", min_length=11, max_length=11)
    avatarUrl: HttpUrl = Body(None, description="用户头像地址")
    status: bool = Body(True, description="在职状态")
    roleId: int = Body(None, description="所属的角色ID")
    affiliationId: int = Body(..., description="用户所属的关系")

    # noinspection PyNestedDecorators
    @field_validator("mobile", mode="after")
    @classmethod
    def valid_mobile(cls, mobile: str) -> str:
        if not validate.phone_number(mobile):
            raise ValueError("手机号错误")

        return mobile


class CreateUserRequest(UserBaseRequest):
    """创建用户请求模型"""

    password: str = Body(..., description="密码")  # RSA 加密后的密码


class UpdateUserInfoRequest(UserBaseRequest):
    """更改用户信息请求模型"""

    id: int = Body(..., description="用户ID")


class UpdatePasswordRequest(CustomModel):
    """修改密码的请求模型"""

    id: int = Body(..., deprecated="用户ID")
    oldPassword: str = Body(..., description="旧的密码")
    newPassword: str = Body(..., description="新的密码")


class AuthGetMenuRequest(GeneralKeywordRequestModel):
    """获取权限菜单请求体"""

    nodeId: int = Body(0, description="节点ID")


class AuthEditMenuRequest(CustomModel):
    """修改权限菜单请求体"""

    id: int = Body(None, description="菜单ID")
    name: str = Body(..., description="菜单名称")
    identifier: str = Body(..., description="菜单标识符")
    nodeId: int = Body(0, description="所属节点ID")


class AuthEditRoleRequest(CustomModel):
    """修改角色信息请求体"""

    id: int = Body(None, description="角色ID")
    name: str = Body(..., description="角色名称")
    identifier: str = Body(..., description="角色标识符")
    menuIdentifierList: list[str] = Body(..., description="菜单权限标识符")


class AuthGetRoleListRequest(GeneralKeywordPageRequestModel):
    """获取角色列表的请求体"""


class AuthEditAffiliationRequest(CustomModel):
    """修改/新增 所属关系的请求体"""

    id: int = Body(None, description="所属关系ID")
    name: str = Body(..., description="所属关系名称")
    nodeId: int = Body(0, description="所属节点ID")


class AuthGetAffiliationListRequest(GeneralKeywordRequestModel):
    """获取所属关系列表的请求体"""

    nodeId: int = Body(0, description="节点ID")
