
from datetime import datetime, timedelta
from typing import Any, TypeVar, Generic
from zoneinfo import ZoneInfo
from time import time

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict, model_validator, Field

import re

T = TypeVar("T")


def convert_datetime_to_gmt(dt: datetime) -> str:
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.strftime("%Y-%m-%d %H:%M:%S")


class CustomModel(BaseModel):
    """ 通用模型 """
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: convert_datetime_to_gmt},
        populate_by_name=True
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

    def serializable_dict(self) -> dict:
        """
        返回一个兼容 JSON 类型的字典
        :return:
        """
        default_dict = self.model_dump()

        return jsonable_encoder(default_dict)

    @property
    def params(self) -> dict:
        """
        将 驼峰体命名风格 转换为 下换线命名模式
        适用于请求体和入参相同的情况
        并不推荐使用, 目前是基于 FastApi Body 中的过滤才可以使用
        :return:
        """
        body = self.serializable_dict()

        def camel_to_snake_case(name):
            # 使用正则表达式将驼峰命名转换为下划线命名
            s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
            return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

        return {camel_to_snake_case(k): v for k, v in body.items()} if isinstance(body, dict) else {}


class PageRequestModel(CustomModel):
    """ 通用分页请求 """
    page: int = Field(1, description="当前页")
    pageSize: int = Field(20, description="每页的数据数量")


class GeneralKeywordRequestModel(CustomModel):
    """ 通用带有关键字且不带分页的请求体 """
    keyword: str = Field("", description="查询关键字")


class GeneralKeywordPageRequestModel(PageRequestModel):
    """ 通用带有关键字和分页的请求体 """
    keyword: str = Field("", description="查询关键字")


class DeleteRequestModel(CustomModel):
    """ 通用删除请求 """
    id: int = Field(..., description="要删除的数据ID")


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
