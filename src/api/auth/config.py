# _author: Coke
# _date: 2024/7/26 14:19
# _description: 验证相关配置信息

from typing import Any

from cryptography.hazmat.primitives.asymmetric import rsa
from pydantic_settings import BaseSettings

from .security import generate_rsa_key_pair


class AuthConfig(BaseSettings):
    """用户认证配置"""

    JWT_ALG: str

    ACCESS_TOKEN_KEY: str  # Access Token 签名
    ACCESS_TOKEN_EXP: int = 60 * 24 * 1  # Access Token 有效期

    REFRESH_TOKEN_KEY: str  # Refresh Token 签名
    REFRESH_TOKEN_EXP: int = 60 * 24 * 7  # Refresh Token 有效期

    SECURE_COOKIES: bool = True

    PRIVATE_KEY: rsa.RSAPrivateKey | None = None  # 私钥
    PUBLIC_KEY: rsa.RSAPublicKey | None = None  # 公钥

    def __init__(self, **values: Any):
        super().__init__(**values)
        self.PRIVATE_KEY, self.PUBLIC_KEY = generate_rsa_key_pair()


auth_config = AuthConfig()
