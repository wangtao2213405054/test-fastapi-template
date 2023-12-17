
from datetime import datetime, timedelta
from typing import Any, TypeVar, Generic
from zoneinfo import ZoneInfo
from time import time

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

    # noinspection PyNestedDecorators
    @model_validator(mode="before")
    @classmethod
    def set_null_microseconds(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        将继承与此中包含 datetime 类中的微秒部分置为 0
        :param data:
        :return:
        """
        datetime_fields = {
            k: v.replace(microsecond=0)
            for k, v in data.items()
            if isinstance(v, datetime)
        }

        return {**data, **datetime_fields}

    def serializable_dict(self):
        """
        返回一个兼容 JSON 类型的字典
        :return:
        """
        default_dict = self.model_dump()

        return jsonable_encoder(default_dict)


class ResponseModel(BaseModel, Generic[T]):
    """ 接口通用返回模型 """
    code: int = Field(200, description="状态码")
    ts: int = Field(int(time()), description="当前响应时间戳")
    message: str = Field("接口请求成功", description="消息体")
    data: T = Field(None, description="返回的数据信息")

    def __init__(self, **kwargs):
        super(ResponseModel, self).__init__(**kwargs)
        self.ts = int(time())


class RedisData(CustomModel):
    """ Redis 数据模型 """
    key: bytes | str
    value: bytes | str
    ttl: int | timedelta | None = None
