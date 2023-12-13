
from datetime import datetime, timedelta
from typing import Any, TypeVar, Generic
from zoneinfo import ZoneInfo

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict, model_validator, Field


T = TypeVar("T")


def convert_datetime_to_gmt(dt: datetime) -> str:
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))

    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


class CustomModel(BaseModel):
    """ 通用模型 """
    model_config = ConfigDict(
        json_encoders={datetime: convert_datetime_to_gmt},
        populate_by_name=True,
    )

    @classmethod
    @model_validator(mode="before")
    def set_null_microseconds(cls, data: dict[str, Any]) -> dict[str, Any]:
        datetime_fields = {
            k: v.replace(microsecond=0)
            for k, v in data.items()
            if isinstance(k, datetime)
        }

        return {**data, **datetime_fields}

    def serializable_dict(self, **kwargs):
        """Return a dict which contains only serializable fields."""
        default_dict = self.model_dump()

        return jsonable_encoder(default_dict)


class ResponseModel(CustomModel, Generic[T]):
    """ 接口通用返回模型 """
    code: int = Field(200, description="状态码")
    message: str = Field("接口请求成功", description="消息体")
    data: T = Field(None, description="返回的数据信息")


class RedisData(CustomModel):
    """ Redis 数据模型 """
    key: bytes | str
    value: bytes | str
    ttl: int | timedelta | None = None
