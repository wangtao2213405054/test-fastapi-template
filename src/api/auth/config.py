# _author: Coke
# _date: 2024/7/26 14:19
# _description: 验证相关配置信息

from pydantic_settings import BaseSettings
from .security import generate_rsa_key_pair
from cryptography.hazmat.primitives.asymmetric import rsa
from typing import Any


class AuthConfig(BaseSettings):
    JWT_ALG: str
    JWT_SECRET: str
    JWT_EXP: int = 5  # minutes

    REFRESH_TOKEN_KEY: str = "refreshToken"
    REFRESH_TOKEN_EXP: int = 60 * 60 * 24 * 1  # 1 day

    SECURE_COOKIES: bool = True

    PRIVATE_KEY: rsa.RSAPrivateKey | None = None
    PUBLIC_KEY: rsa.RSAPublicKey | None = None

    def __init__(self, **values: Any):
        super().__init__(**values)
        self.PRIVATE_KEY, self.PUBLIC_KEY = generate_rsa_key_pair()  # 私钥, 公钥


auth_config = AuthConfig()
