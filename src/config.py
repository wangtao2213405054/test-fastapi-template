# _author: Coke
# _date: 2024/7/25 22:16
# _description: 项目依赖项

from typing import Any

from pydantic import MySQLDsn, RedisDsn, model_validator
from pydantic_settings import BaseSettings

from src.constants import Environment

from .exceptions import PermissionDenied


class Config(BaseSettings):
    DATABASE_URL: MySQLDsn  # Mysql 数据库地址
    REDIS_URL: RedisDsn  # Redis 数据库地址

    SITE_DOMAIN: str = "myapp.com"  # 当前地址

    ENVIRONMENT: Environment = Environment.PRODUCTION  # 当前环境

    SENTRY_DSN: str | None = None  # Sentry 服务的 DSN KEY

    CORS_ORIGINS: list[str]  # 允许跨域的来源
    CORS_ORIGINS_REGEX: str | None = None  # 允许的来源的正则表达式
    CORS_HEADERS: list[str]  # 允许的标头列表

    APP_VERSION: str = "1"  # 当前的应用版本

    LOGGING_LEVEL: str = "INFO"  # 日志等级

    PREFIX: str = "/api/v1/client"  # http 请求前缀

    SOCKET_PREFIX: str = "/socket/v1/client"  # socket 请求前缀

    @model_validator(mode="after")
    def validate_sentry_non_local(self) -> "Config":
        """校验 Sentry 服务是否启动"""
        if self.ENVIRONMENT.is_deployed and not self.SENTRY_DSN:
            raise ValueError("Sentry (错误跟踪和监控)服务没有设置")

        return self


settings = Config()

app_configs: dict[str, Any] = {"title": "接口文档"}
if settings.ENVIRONMENT.is_deployed:
    app_configs["root_path"] = f"/v{settings.APP_VERSION}"

if not settings.ENVIRONMENT.is_debug:
    app_configs["openapi_url"] = None  # hide docs


def debug() -> None:
    """
    判断当前环境是否为 DEBUG, 如果不为真则抛出异常

    :return:
    """

    if not settings.ENVIRONMENT.is_debug:
        raise PermissionDenied()
