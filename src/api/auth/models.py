# _author: Coke
# _date: 2024/8/26 下午3:22
# _description: 用户认证相关数据库响应模型

from src.models.types import CustomModel

from .types import RefreshTokenRequest


class AccessTokenResponse(RefreshTokenRequest):
    """登录的响应结构"""

    accessToken: str


class SwaggerToken(CustomModel):
    """Swagger 登录的响应结构"""

    access_token: str
    token_type: str
